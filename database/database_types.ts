/**
 * Database Type Definitions for Oover (Sport Prediction App)
 * 
 * This file contains TypeScript type definitions for all database tables
 * and their relationships. Use these types for type-safe database operations
 * with Supabase.
 * 
 * @version 1.0.0
 * @date 2025-10-27
 */

// ============================================================================
// ENUM DEFINITIONS
// ============================================================================

/**
 * User roles in the system
 */
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  MODERATOR = 'moderator'
}

/**
 * Match status
 */
export enum MatchStatus {
  SCHEDULED = 'scheduled',
  LIVE = 'live',
  FINISHED = 'finished',
  POSTPONED = 'postponed',
  CANCELLED = 'cancelled'
}

/**
 * Prediction outcome status
 */
export enum PredictionOutcome {
  PENDING = 'pending',
  WON = 'won',
  LOST = 'lost',
  VOID = 'void'
}

// ============================================================================
// COUNTRY TYPES
// ============================================================================

/**
 * Country entity - represents a country or international organization
 */
export interface Country {
  /** Unique identifier (e.g., 'tr', 'gb', 'uefa') */
  id: string;
  
  /** Full country name (e.g., 'Turkey', 'England') */
  name: string;
  
  /** ISO 3166-1 alpha-2 country code (e.g., 'TR', 'GB') or organization code */
  code: string | null;
  
  /** Country flag emoji or URL */
  flag: string | null;
  
  /** True for international organizations (UEFA, FIFA, etc.) */
  is_international: boolean;
  
  /** Active status flag */
  is_active: boolean;
  
  /** Record creation timestamp */
  created_at: string;
  
  /** Record last update timestamp */
  updated_at: string | null;
}

/**
 * Country insert type (for creating new countries)
 */
export interface CountryInsert {
  id: string;
  name: string;
  code?: string | null;
  flag?: string | null;
  is_international?: boolean;
  is_active?: boolean;
}

/**
 * Country update type (for updating existing countries)
 */
export interface CountryUpdate {
  name?: string;
  code?: string | null;
  flag?: string | null;
  is_international?: boolean;
  is_active?: boolean;
  updated_at?: string;
}

/**
 * Country with relationships (includes related leagues and teams)
 */
export interface CountryWithRelations extends Country {
  leagues?: League[];
  teams?: Team[];
}

// ============================================================================
// SPORT TYPES
// ============================================================================

/**
 * Sport entity
 */
export interface Sport {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

// ============================================================================
// LEAGUE TYPES
// ============================================================================

/**
 * League entity
 */
export interface League {
  id: string;
  name: string;
  
  /** @deprecated Use country_id instead */
  country: string | null;
  
  /** Foreign key to countries table */
  country_id: string | null;
  
  season: string | null;
  logo: string | null;
  sport_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * League insert type
 */
export interface LeagueInsert {
  id: string;
  name: string;
  country_id?: string | null;
  season?: string | null;
  logo?: string | null;
  sport_id?: string | null;
  is_active?: boolean;
}

/**
 * League update type
 */
export interface LeagueUpdate {
  name?: string;
  country_id?: string | null;
  season?: string | null;
  logo?: string | null;
  sport_id?: string | null;
  is_active?: boolean;
  updated_at?: string;
}

/**
 * League with relationships
 */
export interface LeagueWithRelations extends League {
  country?: Country | null;
  sport?: Sport | null;
  matches?: Match[];
}

// ============================================================================
// TEAM TYPES
// ============================================================================

/**
 * Team entity
 */
export interface Team {
  id: string;
  name: string;
  
  /** @deprecated Use country_id instead */
  country: string | null;
  
  /** Foreign key to countries table */
  country_id: string | null;
  
  logo: string | null;
  is_national: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * Team insert type
 */
export interface TeamInsert {
  id: string;
  name: string;
  country_id?: string | null;
  logo?: string | null;
  is_national?: boolean;
  is_active?: boolean;
}

/**
 * Team update type
 */
export interface TeamUpdate {
  name?: string;
  country_id?: string | null;
  logo?: string | null;
  is_national?: boolean;
  is_active?: boolean;
  updated_at?: string;
}

/**
 * Team with relationships
 */
export interface TeamWithRelations extends Team {
  country?: Country | null;
  home_matches?: Match[];
  away_matches?: Match[];
}

// ============================================================================
// MATCH TYPES
// ============================================================================

/**
 * Match entity
 */
export interface Match {
  id: string;
  league_id: string | null;
  home_team_id: string | null;
  away_team_id: string | null;
  match_date: string;
  match_time: string | null;
  home_score: number | null;
  away_score: number | null;
  status: MatchStatus;
  venue: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * Match insert type
 */
export interface MatchInsert {
  id: string;
  league_id?: string | null;
  home_team_id?: string | null;
  away_team_id?: string | null;
  match_date: string;
  match_time?: string | null;
  home_score?: number | null;
  away_score?: number | null;
  status?: MatchStatus;
  venue?: string | null;
  is_active?: boolean;
}

/**
 * Match update type
 */
export interface MatchUpdate {
  league_id?: string | null;
  home_team_id?: string | null;
  away_team_id?: string | null;
  match_date?: string;
  match_time?: string | null;
  home_score?: number | null;
  away_score?: number | null;
  status?: MatchStatus;
  venue?: string | null;
  is_active?: boolean;
  updated_at?: string;
}

/**
 * Match with relationships
 */
export interface MatchWithRelations extends Match {
  league?: LeagueWithRelations | null;
  home_team?: TeamWithRelations | null;
  away_team?: TeamWithRelations | null;
  predictions?: Prediction[];
}

// ============================================================================
// USER TYPES
// ============================================================================

/**
 * User entity
 */
export interface User {
  id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  avatar_url: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * User insert type
 */
export interface UserInsert {
  id: string;
  email: string;
  username?: string | null;
  full_name?: string | null;
  avatar_url?: string | null;
  role?: UserRole;
  is_active?: boolean;
}

/**
 * User update type
 */
export interface UserUpdate {
  email?: string;
  username?: string | null;
  full_name?: string | null;
  avatar_url?: string | null;
  role?: UserRole;
  is_active?: boolean;
  updated_at?: string;
}

// ============================================================================
// PREDICTION TYPES
// ============================================================================

/**
 * Prediction entity
 */
export interface Prediction {
  id: string;
  user_id: string | null;
  match_id: string | null;
  predicted_home_score: number | null;
  predicted_away_score: number | null;
  confidence: number | null;
  outcome: PredictionOutcome;
  points_earned: number | null;
  created_at: string;
  updated_at: string | null;
}

/**
 * Prediction insert type
 */
export interface PredictionInsert {
  id: string;
  user_id?: string | null;
  match_id?: string | null;
  predicted_home_score?: number | null;
  predicted_away_score?: number | null;
  confidence?: number | null;
  outcome?: PredictionOutcome;
  points_earned?: number | null;
}

/**
 * Prediction update type
 */
export interface PredictionUpdate {
  predicted_home_score?: number | null;
  predicted_away_score?: number | null;
  confidence?: number | null;
  outcome?: PredictionOutcome;
  points_earned?: number | null;
  updated_at?: string;
}

/**
 * Prediction with relationships
 */
export interface PredictionWithRelations extends Prediction {
  user?: User | null;
  match?: MatchWithRelations | null;
}

// ============================================================================
// DATABASE INTERFACE
// ============================================================================

/**
 * Complete database schema interface for Supabase
 */
export interface Database {
  public: {
    Tables: {
      countries: {
        Row: Country;
        Insert: CountryInsert;
        Update: CountryUpdate;
      };
      sports: {
        Row: Sport;
        Insert: Omit<Sport, 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Sport, 'id' | 'created_at'>>;
      };
      leagues: {
        Row: League;
        Insert: LeagueInsert;
        Update: LeagueUpdate;
      };
      teams: {
        Row: Team;
        Insert: TeamInsert;
        Update: TeamUpdate;
      };
      matches: {
        Row: Match;
        Insert: MatchInsert;
        Update: MatchUpdate;
      };
      users: {
        Row: User;
        Insert: UserInsert;
        Update: UserUpdate;
      };
      predictions: {
        Row: Prediction;
        Insert: PredictionInsert;
        Update: PredictionUpdate;
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      user_role: UserRole;
      match_status: MatchStatus;
      prediction_outcome: PredictionOutcome;
    };
  };
}

// ============================================================================
// QUERY FILTER TYPES
// ============================================================================

/**
 * Country filter options
 */
export interface CountryFilter {
  is_active?: boolean;
  is_international?: boolean;
  code?: string;
  name?: string;
}

/**
 * League filter options
 */
export interface LeagueFilter {
  is_active?: boolean;
  country_id?: string;
  sport_id?: string;
  season?: string;
}

/**
 * Team filter options
 */
export interface TeamFilter {
  is_active?: boolean;
  country_id?: string;
  is_national?: boolean;
}

/**
 * Match filter options
 */
export interface MatchFilter {
  status?: MatchStatus;
  league_id?: string;
  home_team_id?: string;
  away_team_id?: string;
  date_from?: string;
  date_to?: string;
}

/**
 * Prediction filter options
 */
export interface PredictionFilter {
  user_id?: string;
  match_id?: string;
  outcome?: PredictionOutcome;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  count?: number;
}

/**
 * Paginated API response
 */
export interface PaginatedResponse<T> {
  data: T[];
  error: string | null;
  count: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Type for Supabase select queries with relations
 */
export type SelectWithRelations<T> = T & {
  [K in keyof T]?: T[K] extends (infer U)[] ? SelectWithRelations<U>[] : SelectWithRelations<T[K]>;
};

/**
 * Type for creating records (excludes auto-generated fields)
 */
export type CreateInput<T> = Omit<T, 'created_at' | 'updated_at'>;

/**
 * Type for updating records (all fields optional except id)
 */
export type UpdateInput<T> = Partial<Omit<T, 'id' | 'created_at'>>;

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/**
 * Example 1: Fetching countries with type safety
 * 
 * ```typescript
 * import { createClient } from '@supabase/supabase-js';
 * import type { Database, Country } from './database_types';
 * 
 * const supabase = createClient<Database>(url, key);
 * 
 * const { data: countries, error } = await supabase
 *   .from('countries')
 *   .select('*')
 *   .eq('is_active', true);
 * 
 * // countries is typed as Country[] | null
 * ```
 */

/**
 * Example 2: Fetching leagues with country relation
 * 
 * ```typescript
 * const { data: leagues, error } = await supabase
 *   .from('leagues')
 *   .select(`
 *     *,
 *     country:countries(*)
 *   `)
 *   .eq('is_active', true);
 * 
 * // leagues is typed as LeagueWithRelations[] | null
 * ```
 */

/**
 * Example 3: Creating a new country
 * 
 * ```typescript
 * const newCountry: CountryInsert = {
 *   id: 'nl',
 *   name: 'Netherlands',
 *   code: 'NL',
 *   flag: '🇳🇱',
 *   is_active: true
 * };
 * 
 * const { data, error } = await supabase
 *   .from('countries')
 *   .insert(newCountry)
 *   .select()
 *   .single();
 * ```
 */

/**
 * Example 4: Updating a country
 * 
 * ```typescript
 * const update: CountryUpdate = {
 *   flag: '🇹🇷',
 *   updated_at: new Date().toISOString()
 * };
 * 
 * const { data, error } = await supabase
 *   .from('countries')
 *   .update(update)
 *   .eq('id', 'tr')
 *   .select()
 *   .single();
 * ```
 */

/**
 * Example 5: Complex query with multiple relations
 * 
 * ```typescript
 * const { data: matches, error } = await supabase
 *   .from('matches')
 *   .select(`
 *     *,
 *     league:leagues(
 *       *,
 *       country:countries(*)
 *     ),
 *     home_team:teams!matches_home_team_id_fkey(*),
 *     away_team:teams!matches_away_team_id_fkey(*)
 *   `)
 *   .eq('status', 'scheduled')
 *   .gte('match_date', '2025-10-27');
 * 
 * // matches is typed as MatchWithRelations[] | null
 * ```
 */

export default Database;
