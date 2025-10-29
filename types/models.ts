/**
 * TypeScript Models
 * 
 * Type definitions for API responses and requests.
 * These match the Django REST Framework serializers.
 */

/**
 * Base Model Interface
 * 
 * Common fields for all models
 */
export interface BaseModel {
  id: string
  created_at: string
  updated_at: string
}

/**
 * Paginated Response Interface
 * 
 * Standard pagination response from Django REST Framework
 */
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

/**
 * Country Model
 * 
 * Represents a country entity
 */
export interface Country extends BaseModel {
  name: string
  code: string
  flag_url: string | null
  is_active: boolean
}

/**
 * League Model
 * 
 * Represents a football league entity
 */
export interface League extends BaseModel {
  name: string
  country_id: string
  country_name?: string // Populated by serializer
  season: string
  logo_url: string | null
  type: 'league' | 'cup'
  is_active: boolean
}

/**
 * Team Model
 * 
 * Represents a football team entity
 */
export interface Team extends BaseModel {
  name: string
  country_id: string
  country_name?: string // Populated by serializer
  league_id: string
  league_name?: string // Populated by serializer
  logo_url: string | null
  founded: number | null
  venue: string | null
  is_active: boolean
}

/**
 * Match Model
 * 
 * Represents a football match entity
 */
export interface Match extends BaseModel {
  league_id: string
  league_name?: string // Populated by serializer
  home_team_id: string
  home_team_name?: string // Populated by serializer
  away_team_id: string
  away_team_name?: string // Populated by serializer
  match_date: string
  status: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled'
  home_score: number | null
  away_score: number | null
  venue: string | null
  referee: string | null
}

/**
 * Prediction Model
 * 
 * Represents a match prediction entity
 */
export interface Prediction extends BaseModel {
  match_id: string
  match_details?: Match // Populated by serializer
  predicted_winner: 'home' | 'draw' | 'away'
  predicted_home_score: number | null
  predicted_away_score: number | null
  confidence: number // 0-100
  actual_winner: 'home' | 'draw' | 'away' | null
  is_correct: boolean | null
}

/**
 * User Model
 * 
 * Represents a user entity
 */
export interface User extends BaseModel {
  email: string
  username: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  avatar_url: string | null
}

/**
 * API Query Parameters
 */
export interface QueryParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: any
}

/**
 * Country Query Parameters
 */
export interface CountryQueryParams extends QueryParams {
  is_active?: boolean
  code?: string
}

/**
 * League Query Parameters
 */
export interface LeagueQueryParams extends QueryParams {
  country?: string
  season?: string
  type?: 'league' | 'cup'
  is_active?: boolean
}

/**
 * Team Query Parameters
 */
export interface TeamQueryParams extends QueryParams {
  country?: string
  league?: string
  is_active?: boolean
}

/**
 * Match Query Parameters
 */
export interface MatchQueryParams extends QueryParams {
  league?: string
  home_team?: string
  away_team?: string
  status?: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled'
  date_from?: string
  date_to?: string
}

/**
 * Prediction Query Parameters
 */
export interface PredictionQueryParams extends QueryParams {
  match?: string
  is_correct?: boolean
}

/**
 * Create/Update DTOs (Data Transfer Objects)
 */
export interface CreateCountryDto {
  name: string
  code: string
  flag_url?: string | null
  is_active?: boolean
}

export interface UpdateCountryDto extends Partial<CreateCountryDto> {}

export interface CreateLeagueDto {
  name: string
  country_id: string
  season: string
  logo_url?: string | null
  type: 'league' | 'cup'
  is_active?: boolean
}

export interface UpdateLeagueDto extends Partial<CreateLeagueDto> {}

export interface CreateTeamDto {
  name: string
  country_id: string
  league_id: string
  logo_url?: string | null
  founded?: number | null
  venue?: string | null
  is_active?: boolean
}

export interface UpdateTeamDto extends Partial<CreateTeamDto> {}

export interface CreateMatchDto {
  league_id: string
  home_team_id: string
  away_team_id: string
  match_date: string
  venue?: string | null
  referee?: string | null
}

export interface UpdateMatchDto extends Partial<CreateMatchDto> {
  status?: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled'
  home_score?: number | null
  away_score?: number | null
}

export interface CreatePredictionDto {
  match_id: string
  predicted_winner: 'home' | 'draw' | 'away'
  predicted_home_score?: number | null
  predicted_away_score?: number | null
  confidence: number
}

export interface UpdatePredictionDto extends Partial<CreatePredictionDto> {
  actual_winner?: 'home' | 'draw' | 'away' | null
  is_correct?: boolean | null
}
