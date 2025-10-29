'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useLeague, useCreateLeague, useUpdateLeague } from '@/hooks/api/use-leagues'
import { Button } from '@/components/ui/button'
import type { CreateLeagueDto, UpdateLeagueDto } from '@/types/models'

/**
 * LeagueForm - Shared form component for creating and editing leagues
 * 
 * Features:
 * - Dual mode (create/edit) based on ID presence
 * - Form validation
 * - Loading states
 * - Error handling
 * - Auto-fill for edit mode
 * - Submit/Cancel actions
 * - Type-safe form data
 * 
 * @param id - League UUID (optional, for edit mode)
 * @param mode - Form mode: 'create' or 'edit'
 * 
 * @example
 * ```tsx
 * // Create mode
 * <LeagueForm mode="create" />
 * 
 * // Edit mode
 * <LeagueForm mode="edit" id="league-uuid" />
 * ```
 */
interface LeagueFormProps {
  mode: 'create' | 'edit'
  id?: string
}

interface FormData {
  name: string
  sport: string
  country: string
  external_id: string
  logo: string
  is_active: boolean
}

export function LeagueForm({ mode, id }: LeagueFormProps) {
  const router = useRouter()

  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    sport: '',
    country: '',
    external_id: '',
    logo: '',
    is_active: true,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch existing league data for edit mode
  const { data: league, isLoading: isLoadingLeague } = useLeague(id || '', {
    enabled: mode === 'edit' && !!id,
  })

  // Mutations
  const createLeague = useCreateLeague()
  const updateLeague = useUpdateLeague()

  // Populate form in edit mode
  useEffect(() => {
    if (mode === 'edit' && league) {
      setFormData({
        name: league.name,
        sport: league.sport,
        country: league.country || '',
        external_id: league.external_id || '',
        logo: league.logo || '',
        is_active: league.is_active,
      })
    }
  }, [mode, league])

  /**
   * Handle input changes
   */
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked
        : value,
    }))

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  /**
   * Validate form data
   */
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'League name is required'
    }

    if (!formData.sport) {
      newErrors.sport = 'Sport is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    try {
      if (mode === 'create') {
        // Create new league
        const data: CreateLeagueDto = {
          name: formData.name.trim(),
          sport: formData.sport,
          country: formData.country || undefined,
          external_id: formData.external_id || undefined,
          logo: formData.logo || undefined,
          is_active: formData.is_active,
        }

        const newLeague = await createLeague.mutateAsync(data)
        router.push(`/admin/leagues/${newLeague.id}`)
      } else if (id) {
        // Update existing league (sport is immutable, cannot be changed)
        const data: UpdateLeagueDto = {
          name: formData.name.trim(),
          country: formData.country || undefined,
          external_id: formData.external_id || undefined,
          logo: formData.logo || undefined,
          is_active: formData.is_active,
        }

        await updateLeague.mutateAsync({ id, data })
        router.push(`/admin/leagues/${id}`)
      }
    } catch (error) {
      console.error('Form submission error:', error)
      alert('Failed to save league. Please try again.')
    }
  }

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    if (mode === 'edit' && id) {
      router.push(`/admin/leagues/${id}`)
    } else {
      router.push('/admin/leagues')
    }
  }

  // Loading state for edit mode
  if (mode === 'edit' && isLoadingLeague) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3" />
          <div className="space-y-3">
            <div className="h-10 bg-muted rounded" />
            <div className="h-10 bg-muted rounded" />
            <div className="h-10 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  const isSubmitting = createLeague.isPending || updateLeague.isPending

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">
          {mode === 'create' ? 'Create League' : 'Edit League'}
        </h1>
        <p className="text-muted-foreground mt-2">
          {mode === 'create'
            ? 'Add a new league to the system'
            : 'Update league information'}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          {/* League Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              League Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.name ? 'border-destructive' : 'border-input'
              }`}
              placeholder="e.g., Premier League"
              required
            />
            {errors.name && (
              <p className="text-sm text-destructive mt-1">{errors.name}</p>
            )}
          </div>

          {/* Sport (Dropdown - will need Sports API) */}
          <div>
            <label htmlFor="sport" className="block text-sm font-medium mb-2">
              Sport <span className="text-destructive">*</span>
            </label>
            <select
              id="sport"
              name="sport"
              value={formData.sport}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.sport ? 'border-destructive' : 'border-input'
              }`}
              required
              disabled={mode === 'edit'}
            >
              <option value="">Select a sport</option>
              <option value="football-uuid">Football</option>
              <option value="basketball-uuid">Basketball</option>
              {/* TODO: Replace with dynamic sports from API */}
            </select>
            {errors.sport && (
              <p className="text-sm text-destructive mt-1">{errors.sport}</p>
            )}
            {mode === 'edit' ? (
              <p className="text-xs text-muted-foreground mt-1">
                Note: Sport cannot be changed after creation
              </p>
            ) : (
              <p className="text-xs text-muted-foreground mt-1">
                Note: Sport options will be loaded from API
              </p>
            )}
          </div>

          {/* Country (Dropdown - will need Countries API) */}
          <div>
            <label htmlFor="country" className="block text-sm font-medium mb-2">
              Country
            </label>
            <select
              id="country"
              name="country"
              value={formData.country}
              onChange={handleChange}
              className="w-full rounded-md border border-input px-3 py-2 text-sm"
            >
              <option value="">International (No Country)</option>
              <option value="england-uuid">England</option>
              <option value="spain-uuid">Spain</option>
              {/* TODO: Replace with dynamic countries from API */}
            </select>
            <p className="text-xs text-muted-foreground mt-1">
              Leave empty for international competitions. Options will be loaded from API.
            </p>
          </div>
        </div>

        {/* Additional Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Additional Information</h2>

          {/* External ID */}
          <div>
            <label htmlFor="external_id" className="block text-sm font-medium mb-2">
              External API ID
            </label>
            <input
              type="text"
              id="external_id"
              name="external_id"
              value={formData.external_id}
              onChange={handleChange}
              className="w-full rounded-md border border-input px-3 py-2 text-sm font-mono"
              placeholder="e.g., 39"
            />
            <p className="text-xs text-muted-foreground mt-1">
              ID from external API (e.g., API-Football)
            </p>
          </div>

          {/* Logo URL */}
          <div>
            <label htmlFor="logo" className="block text-sm font-medium mb-2">
              Logo URL
            </label>
            <input
              type="url"
              id="logo"
              name="logo"
              value={formData.logo}
              onChange={handleChange}
              className="w-full rounded-md border border-input px-3 py-2 text-sm"
              placeholder="https://example.com/logo.png"
            />
            {formData.logo && (
              <div className="mt-2">
                <img
                  src={formData.logo}
                  alt="Logo preview"
                  className="w-16 h-16 object-contain rounded border"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
              </div>
            )}
          </div>

          {/* Active Status */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 rounded border-input"
            />
            <label htmlFor="is_active" className="text-sm font-medium">
              League is active
            </label>
          </div>
          <p className="text-xs text-muted-foreground">
            Inactive leagues won't appear in public listings
          </p>
        </div>

        {/* Form Actions */}
        <div className="flex items-center gap-3 justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? mode === 'create'
                ? 'Creating...'
                : 'Saving...'
              : mode === 'create'
              ? 'Create League'
              : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  )
}
