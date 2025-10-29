'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTeam, useCreateTeam, useUpdateTeam } from '@/hooks/api/use-teams'
import { Button } from '@/components/ui/button'
import type { CreateTeamDto, UpdateTeamDto } from '@/types/models'

/**
 * TeamForm - Shared form component for creating and editing teams
 * 
 * Features:
 * - Dual mode (create/edit) based on ID presence
 * - Form validation
 * - Loading states
 * - Error handling
 * - Auto-fill for edit mode
 * - Submit/Cancel actions
 * - Type-safe form data
 * - Team-specific fields: code, website, market_value, founded
 * 
 * @param id - Team ID (optional, for edit mode)
 * @param mode - Form mode: 'create' or 'edit'
 * 
 * @example
 * ```tsx
 * // Create mode
 * <TeamForm mode="create" />
 * 
 * // Edit mode
 * <TeamForm mode="edit" id="team-id" />
 * ```
 */
interface TeamFormProps {
  mode: 'create' | 'edit'
  id?: string
}

interface FormData {
  name: string
  code: string
  country_id: string
  external_id: string
  logo: string
  founded: string
  website: string
  market_value: string
  is_active: boolean
}

export function TeamForm({ mode, id }: TeamFormProps) {
  const router = useRouter()

  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    code: '',
    country_id: '',
    external_id: '',
    logo: '',
    founded: '',
    website: '',
    market_value: '',
    is_active: true,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch existing team data for edit mode
  const { data: team, isLoading: isLoadingTeam } = useTeam(id || '', {
    enabled: mode === 'edit' && !!id,
  })

  // Mutations
  const createTeam = useCreateTeam()
  const updateTeam = useUpdateTeam()

  // Populate form in edit mode
  useEffect(() => {
    if (mode === 'edit' && team) {
      setFormData({
        name: team.name,
        code: team.code,
        country_id: team.country_id || '',
        external_id: team.external_id || '',
        logo: team.logo || '',
        founded: team.founded?.toString() || '',
        website: team.website || '',
        market_value: team.market_value?.toString() || '',
        is_active: team.is_active,
      })
    }
  }, [mode, team])

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
      newErrors.name = 'Team name is required'
    }

    if (!formData.code.trim()) {
      newErrors.code = 'Team code is required'
    } else if (formData.code.length !== 3) {
      newErrors.code = 'Team code must be exactly 3 characters'
    } else if (!/^[A-Z]{3}$/.test(formData.code)) {
      newErrors.code = 'Team code must be 3 uppercase letters (e.g., MUN, BAR)'
    }

    if (!formData.country_id) {
      newErrors.country_id = 'Country is required'
    }

    if (formData.founded && (parseInt(formData.founded) < 1800 || parseInt(formData.founded) > new Date().getFullYear())) {
      newErrors.founded = 'Founded year must be between 1800 and current year'
    }

    if (formData.website && !formData.website.match(/^https?:\/\/.+/)) {
      newErrors.website = 'Website must be a valid URL (starting with http:// or https://)'
    }

    if (formData.market_value && (parseInt(formData.market_value) < 0 || isNaN(parseInt(formData.market_value)))) {
      newErrors.market_value = 'Market value must be a positive number'
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
        // Create new team
        const data: CreateTeamDto = {
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          country_id: formData.country_id,
          external_id: formData.external_id || undefined,
          logo: formData.logo || undefined,
          founded: formData.founded ? parseInt(formData.founded) : undefined,
          website: formData.website || undefined,
          market_value: formData.market_value ? parseInt(formData.market_value) : undefined,
          is_active: formData.is_active,
        }

        const newTeam = await createTeam.mutateAsync(data)
        router.push(`/admin/teams/${newTeam.id}`)
      } else if (id) {
        // Update existing team
        const data: UpdateTeamDto = {
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          country_id: formData.country_id || undefined,
          external_id: formData.external_id || undefined,
          logo: formData.logo || undefined,
          founded: formData.founded ? parseInt(formData.founded) : undefined,
          website: formData.website || undefined,
          market_value: formData.market_value ? parseInt(formData.market_value) : undefined,
          is_active: formData.is_active,
        }

        await updateTeam.mutateAsync({ id, data })
        router.push(`/admin/teams/${id}`)
      }
    } catch (error) {
      console.error('Form submission error:', error)
      alert('Failed to save team. Please try again.')
    }
  }

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    if (mode === 'edit' && id) {
      router.push(`/admin/teams/${id}`)
    } else {
      router.push('/admin/teams')
    }
  }

  // Loading state for edit mode
  if (mode === 'edit' && isLoadingTeam) {
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

  const isSubmitting = createTeam.isPending || updateTeam.isPending

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">
          {mode === 'create' ? 'Create Team' : 'Edit Team'}
        </h1>
        <p className="text-muted-foreground mt-2">
          {mode === 'create'
            ? 'Add a new team to the system'
            : 'Update team information'}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          {/* Team Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Team Name <span className="text-destructive">*</span>
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
              placeholder="e.g., Manchester United"
              required
            />
            {errors.name && (
              <p className="text-sm text-destructive mt-1">{errors.name}</p>
            )}
          </div>

          {/* Team Code */}
          <div>
            <label htmlFor="code" className="block text-sm font-medium mb-2">
              Team Code (3 letters) <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              id="code"
              name="code"
              value={formData.code}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm font-mono uppercase ${
                errors.code ? 'border-destructive' : 'border-input'
              }`}
              placeholder="e.g., MUN"
              maxLength={3}
              required
            />
            {errors.code && (
              <p className="text-sm text-destructive mt-1">{errors.code}</p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              3-letter code in uppercase (e.g., MUN, BAR, FCB)
            </p>
          </div>

          {/* Country (Dropdown - will need Countries API) */}
          <div>
            <label htmlFor="country_id" className="block text-sm font-medium mb-2">
              Country <span className="text-destructive">*</span>
            </label>
            <select
              id="country_id"
              name="country_id"
              value={formData.country_id}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.country_id ? 'border-destructive' : 'border-input'
              }`}
              required
            >
              <option value="">Select a country</option>
              <option value="england-uuid">England</option>
              <option value="spain-uuid">Spain</option>
              <option value="germany-uuid">Germany</option>
              {/* TODO: Replace with dynamic countries from API */}
            </select>
            {errors.country_id && (
              <p className="text-sm text-destructive mt-1">{errors.country_id}</p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              Options will be loaded from API
            </p>
          </div>
        </div>

        {/* Team Details */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Team Details</h2>

          {/* Founded Year */}
          <div>
            <label htmlFor="founded" className="block text-sm font-medium mb-2">
              Founded Year
            </label>
            <input
              type="number"
              id="founded"
              name="founded"
              value={formData.founded}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.founded ? 'border-destructive' : 'border-input'
              }`}
              placeholder="e.g., 1878"
              min="1800"
              max={new Date().getFullYear()}
            />
            {errors.founded && (
              <p className="text-sm text-destructive mt-1">{errors.founded}</p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              Year the team was established (1800 - {new Date().getFullYear()})
            </p>
          </div>

          {/* Official Website */}
          <div>
            <label htmlFor="website" className="block text-sm font-medium mb-2">
              Official Website
            </label>
            <input
              type="url"
              id="website"
              name="website"
              value={formData.website}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.website ? 'border-destructive' : 'border-input'
              }`}
              placeholder="https://www.team-website.com"
            />
            {errors.website && (
              <p className="text-sm text-destructive mt-1">{errors.website}</p>
            )}
          </div>

          {/* Market Value */}
          <div>
            <label htmlFor="market_value" className="block text-sm font-medium mb-2">
              Market Value (EUR)
            </label>
            <input
              type="number"
              id="market_value"
              name="market_value"
              value={formData.market_value}
              onChange={handleChange}
              className={`w-full rounded-md border px-3 py-2 text-sm ${
                errors.market_value ? 'border-destructive' : 'border-input'
              }`}
              placeholder="e.g., 500000000"
              min="0"
            />
            {errors.market_value && (
              <p className="text-sm text-destructive mt-1">{errors.market_value}</p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              Total market value in EUR (e.g., 500000000 for €500M)
            </p>
          </div>

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
              placeholder="e.g., 33"
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
              Team is active
            </label>
          </div>
          <p className="text-xs text-muted-foreground">
            Inactive teams won't appear in public listings
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
              ? 'Create Team'
              : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  )
}
