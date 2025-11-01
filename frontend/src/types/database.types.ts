/**
 * Auto-generated TypeScript types for Supabase database schema
 * Generated on: 2025-11-01
 * 
 * DO NOT EDIT MANUALLY - Regenerate using: supabase gen types typescript
 * 
 * This file contains TypeScript definitions for all database tables,
 * including Row (select), Insert, and Update types for each table.
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      _prisma_migrations: {
        Row: {
          applied_steps_count: number
          checksum: string
          finished_at: string | null
          id: string
          logs: string | null
          migration_name: string
          rolled_back_at: string | null
          started_at: string
        }
        Insert: {
          applied_steps_count?: number
          checksum: string
          finished_at?: string | null
          id: string
          logs?: string | null
          migration_name: string
          rolled_back_at?: string | null
          started_at?: string
        }
        Update: {
          applied_steps_count?: number
          checksum?: string
          finished_at?: string | null
          id?: string
          logs?: string | null
          migration_name?: string
          rolled_back_at?: string | null
          started_at?: string
        }
        Relationships: []
      }
      api_sync: {
        Row: {
          completed_at: string | null
          error_message: string
          errors: Json
          id: string
          metadata: Json
          provider: string
          records_created: number
          records_failed: number
          records_processed: number
          records_updated: number
          resource_type: string
          started_at: string
          status: string
        }
        Insert: {
          completed_at?: string | null
          error_message: string
          errors: Json
          id: string
          metadata: Json
          provider: string
          records_created: number
          records_failed: number
          records_processed: number
          records_updated: number
          resource_type: string
          started_at: string
          status: string
        }
        Update: {
          completed_at?: string | null
          error_message?: string
          errors?: Json
          id?: string
          metadata?: Json
          provider?: string
          records_created?: number
          records_failed?: number
          records_processed?: number
          records_updated?: number
          resource_type?: string
          started_at?: string
          status?: string
        }
        Relationships: []
      }
      auth_group: {
        Row: {
          id: number
          name: string
        }
        Insert: {
          id?: number
          name: string
        }
        Update: {
          id?: number
          name?: string
        }
        Relationships: []
      }
      auth_group_permissions: {
        Row: {
          group_id: number
          id: number
          permission_id: number
        }
        Insert: {
          group_id: number
          id?: number
          permission_id: number
        }
        Update: {
          group_id?: number
          id?: number
          permission_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm"
            columns: ["permission_id"]
            isOneToOne: false
            referencedRelation: "auth_permission"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "auth_group"
            referencedColumns: ["id"]
          },
        ]
      }
      auth_permission: {
        Row: {
          codename: string
          content_type_id: number
          id: number
          name: string
        }
        Insert: {
          codename: string
          content_type_id: number
          id?: number
          name: string
        }
        Update: {
          codename?: string
          content_type_id?: number
          id?: number
          name?: string
        }
        Relationships: [
          {
            foreignKeyName: "auth_permission_content_type_id_2f476e4b_fk_django_co"
            columns: ["content_type_id"]
            isOneToOne: false
            referencedRelation: "django_content_type"
            referencedColumns: ["id"]
          },
        ]
      }
      auth_user: {
        Row: {
          date_joined: string
          email: string
          first_name: string
          id: number
          is_active: boolean
          is_staff: boolean
          is_superuser: boolean
          last_login: string | null
          last_name: string
          password: string
          username: string
        }
        Insert: {
          date_joined: string
          email: string
          first_name: string
          id?: number
          is_active: boolean
          is_staff: boolean
          is_superuser: boolean
          last_login?: string | null
          last_name: string
          password: string
          username: string
        }
        Update: {
          date_joined?: string
          email?: string
          first_name?: string
          id?: number
          is_active?: boolean
          is_staff?: boolean
          is_superuser?: boolean
          last_login?: string | null
          last_name?: string
          password?: string
          username?: string
        }
        Relationships: []
      }
      auth_user_groups: {
        Row: {
          group_id: number
          id: number
          user_id: number
        }
        Insert: {
          group_id: number
          id?: number
          user_id: number
        }
        Update: {
          group_id?: number
          id?: number
          user_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "auth_user_groups_group_id_97559544_fk_auth_group_id"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "auth_group"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "auth_user_groups_user_id_6a12ed8b_fk_auth_user_id"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "auth_user"
            referencedColumns: ["id"]
          },
        ]
      }
      auth_user_user_permissions: {
        Row: {
          id: number
          permission_id: number
          user_id: number
        }
        Insert: {
          id?: number
          permission_id: number
          user_id: number
        }
        Update: {
          id?: number
          permission_id?: number
          user_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm"
            columns: ["permission_id"]
            isOneToOne: false
            referencedRelation: "auth_permission"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "auth_user"
            referencedColumns: ["id"]
          },
        ]
      }
      bet_tracking: {
        Row: {
          bet_id: number
          created_at: string | null
          id: number
          notes: string | null
          odds: number | null
          potential_return: number | null
          status: string
          tracked_at: string | null
        }
        Insert: {
          bet_id: number
          created_at?: string | null
          id?: number
          notes?: string | null
          odds?: number | null
          potential_return?: number | null
          status: string
          tracked_at?: string | null
        }
        Update: {
          bet_id?: number
          created_at?: string | null
          id?: number
          notes?: string | null
          odds?: number | null
          potential_return?: number | null
          status?: string
          tracked_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bet_tracking_bet_id_fkey"
            columns: ["bet_id"]
            isOneToOne: false
            referencedRelation: "user_bets"
            referencedColumns: ["id"]
          },
        ]
      }
      betting_markets: {
        Row: {
          category: string
          code: string
          created_at: string | null
          description: string | null
          display_order: number | null
          id: number
          is_active: boolean | null
          name: string
          updated_at: string | null
        }
        Insert: {
          category: string
          code: string
          created_at?: string | null
          description?: string | null
          display_order?: number | null
          id?: number
          is_active?: boolean | null
          name: string
          updated_at?: string | null
        }
        Update: {
          category?: string
          code?: string
          created_at?: string | null
          description?: string | null
          display_order?: number | null
          id?: number
          is_active?: boolean | null
          name?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      betting_tips: {
        Row: {
          actual_result: string | null
          confidence: number
          created_at: string | null
          id: number
          market_id: number
          match_id: string
          prediction: string
          reasoning: string | null
          recommended_odds: number | null
          settled_at: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          actual_result?: string | null
          confidence: number
          created_at?: string | null
          id?: number
          market_id: number
          match_id: string
          prediction: string
          reasoning?: string | null
          recommended_odds?: number | null
          settled_at?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          actual_result?: string | null
          confidence?: number
          created_at?: string | null
          id?: number
          market_id?: number
          match_id?: string
          prediction?: string
          reasoning?: string | null
          recommended_odds?: number | null
          settled_at?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "betting_tips_market_id_fkey"
            columns: ["market_id"]
            isOneToOne: false
            referencedRelation: "betting_markets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "betting_tips_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      bookmakers: {
        Row: {
          country: string | null
          created_at: string | null
          external_id: string | null
          id: number
          is_active: boolean | null
          logo_url: string | null
          name: string
          updated_at: string | null
          website: string | null
        }
        Insert: {
          country?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: number
          is_active?: boolean | null
          logo_url?: string | null
          name: string
          updated_at?: string | null
          website?: string | null
        }
        Update: {
          country?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: number
          is_active?: boolean | null
          logo_url?: string | null
          name?: string
          updated_at?: string | null
          website?: string | null
        }
        Relationships: []
      }
      countries: {
        Row: {
          code: string | null
          created_at: string
          fifa_code: string | null
          flag: string | null
          flag_url: string | null
          id: string
          is_active: boolean
          is_international: boolean
          name: string
          region: string | null
          updated_at: string | null
        }
        Insert: {
          code?: string | null
          created_at?: string
          fifa_code?: string | null
          flag?: string | null
          flag_url?: string | null
          id?: string
          is_active?: boolean
          is_international?: boolean
          name: string
          region?: string | null
          updated_at?: string | null
        }
        Update: {
          code?: string | null
          created_at?: string
          fifa_code?: string | null
          flag?: string | null
          flag_url?: string | null
          id?: string
          is_active?: boolean
          is_international?: boolean
          name?: string
          region?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      data_sync_logs: {
        Row: {
          completedAt: string | null
          createdAt: string
          errorMessage: string | null
          id: string
          metadata: Json | null
          recordsFailed: number
          recordsProcessed: number
          source: string
          startedAt: string
          status: string
          syncType: string
        }
        Insert: {
          completedAt?: string | null
          createdAt?: string
          errorMessage?: string | null
          id: string
          metadata?: Json | null
          recordsFailed?: number
          recordsProcessed?: number
          source: string
          startedAt: string
          status: string
          syncType: string
        }
        Update: {
          completedAt?: string | null
          createdAt?: string
          errorMessage?: string | null
          id?: string
          metadata?: Json | null
          recordsFailed?: number
          recordsProcessed?: number
          source?: string
          startedAt?: string
          status?: string
          syncType?: string
        }
        Relationships: []
      }
      django_admin_log: {
        Row: {
          action_flag: number
          action_time: string
          change_message: string
          content_type_id: number | null
          id: number
          object_id: string | null
          object_repr: string
          user_id: number
        }
        Insert: {
          action_flag: number
          action_time: string
          change_message: string
          content_type_id?: number | null
          id?: number
          object_id?: string | null
          object_repr: string
          user_id: number
        }
        Update: {
          action_flag?: number
          action_time?: string
          change_message?: string
          content_type_id?: number | null
          id?: number
          object_id?: string | null
          object_repr?: string
          user_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "django_admin_log_content_type_id_c4bce8eb_fk_django_co"
            columns: ["content_type_id"]
            isOneToOne: false
            referencedRelation: "django_content_type"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "django_admin_log_user_id_c564eba6_fk_auth_user_id"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "auth_user"
            referencedColumns: ["id"]
          },
        ]
      }
      django_content_type: {
        Row: {
          app_label: string
          id: number
          model: string
        }
        Insert: {
          app_label: string
          id?: number
          model: string
        }
        Update: {
          app_label?: string
          id?: number
          model?: string
        }
        Relationships: []
      }
      django_migrations: {
        Row: {
          app: string
          applied: string
          id: number
          name: string
        }
        Insert: {
          app: string
          applied: string
          id?: number
          name: string
        }
        Update: {
          app?: string
          applied?: string
          id?: number
          name?: string
        }
        Relationships: []
      }
      django_session: {
        Row: {
          expire_date: string
          session_data: string
          session_key: string
        }
        Insert: {
          expire_date: string
          session_data: string
          session_key: string
        }
        Update: {
          expire_date?: string
          session_data?: string
          session_key?: string
        }
        Relationships: []
      }
      leagues: {
        Row: {
          characteristics: Json | null
          code: string | null
          confederation: string | null
          country_id: string | null
          created_at: string
          external_id: string | null
          id: string
          is_active: boolean
          logo: string | null
          name: string
          sport_id: string
          tier: number | null
          updated_at: string
        }
        Insert: {
          characteristics?: Json | null
          code?: string | null
          confederation?: string | null
          country_id?: string | null
          created_at?: string
          external_id?: string | null
          id: string
          is_active?: boolean
          logo?: string | null
          name: string
          sport_id: string
          tier?: number | null
          updated_at: string
        }
        Update: {
          characteristics?: Json | null
          code?: string | null
          confederation?: string | null
          country_id?: string | null
          created_at?: string
          external_id?: string | null
          id?: string
          is_active?: boolean
          logo?: string | null
          name?: string
          sport_id?: string
          tier?: number | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "fk_leagues_country_id"
            columns: ["country_id"]
            isOneToOne: false
            referencedRelation: "countries"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fk_leagues_sport_id"
            columns: ["sport_id"]
            isOneToOne: false
            referencedRelation: "sports"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "leagues_sportId_fkey"
            columns: ["sport_id"]
            isOneToOne: false
            referencedRelation: "sports"
            referencedColumns: ["id"]
          },
        ]
      }
      leagues_backup: {
        Row: {
          country: string | null
          country_id: string | null
          createdAt: string | null
          externalId: string | null
          id: string | null
          isActive: boolean | null
          logo: string | null
          name: string | null
          season: string | null
          sportId: string | null
          updatedAt: string | null
        }
        Insert: {
          country?: string | null
          country_id?: string | null
          createdAt?: string | null
          externalId?: string | null
          id?: string | null
          isActive?: boolean | null
          logo?: string | null
          name?: string | null
          season?: string | null
          sportId?: string | null
          updatedAt?: string | null
        }
        Update: {
          country?: string | null
          country_id?: string | null
          createdAt?: string | null
          externalId?: string | null
          id?: string | null
          isActive?: boolean | null
          logo?: string | null
          name?: string | null
          season?: string | null
          sportId?: string | null
          updatedAt?: string | null
        }
        Relationships: []
      }
      match_analysis: {
        Row: {
          analyzedAt: string
          awayWinProbability: number
          createdAt: string
          drawProbability: number
          formAnalysis: Json | null
          headToHead: Json | null
          homeWinProbability: number
          id: string
          keyFactors: Json | null
          matchId: string
          modelVersion: string | null
          riskLevel: string | null
          updatedAt: string
        }
        Insert: {
          analyzedAt?: string
          awayWinProbability: number
          createdAt?: string
          drawProbability: number
          formAnalysis?: Json | null
          headToHead?: Json | null
          homeWinProbability: number
          id: string
          keyFactors?: Json | null
          matchId: string
          modelVersion?: string | null
          riskLevel?: string | null
          updatedAt: string
        }
        Update: {
          analyzedAt?: string
          awayWinProbability?: number
          createdAt?: string
          drawProbability?: number
          formAnalysis?: Json | null
          headToHead?: Json | null
          homeWinProbability?: number
          id?: string
          keyFactors?: Json | null
          matchId?: string
          modelVersion?: string | null
          riskLevel?: string | null
          updatedAt?: string
        }
        Relationships: [
          {
            foreignKeyName: "match_analysis_matchId_fkey"
            columns: ["matchId"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      match_events: {
        Row: {
          assist_player_id: string | null
          assist_player_name: string | null
          card_type: string | null
          created_at: string | null
          event_details: Json | null
          event_time: number | null
          event_type: string
          external_id: string | null
          extra_time: number | null
          goal_type: string | null
          id: string
          match_id: string | null
          player_name: string | null
          score_away: number | null
          score_home: number | null
          substitution_type: string | null
          team_id: string | null
          team_side: string | null
          updated_at: string | null
        }
        Insert: {
          assist_player_id?: string | null
          assist_player_name?: string | null
          card_type?: string | null
          created_at?: string | null
          event_details?: Json | null
          event_time?: number | null
          event_type: string
          external_id?: string | null
          extra_time?: number | null
          goal_type?: string | null
          id?: string
          match_id?: string | null
          player_name?: string | null
          score_away?: number | null
          score_home?: number | null
          substitution_type?: string | null
          team_id?: string | null
          team_side?: string | null
          updated_at?: string | null
        }
        Update: {
          assist_player_id?: string | null
          assist_player_name?: string | null
          card_type?: string | null
          created_at?: string | null
          event_details?: Json | null
          event_time?: number | null
          event_type?: string
          external_id?: string | null
          extra_time?: number | null
          goal_type?: string | null
          id?: string
          match_id?: string | null
          player_name?: string | null
          score_away?: number | null
          score_home?: number | null
          substitution_type?: string | null
          team_id?: string | null
          team_side?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_events_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_events_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      match_odds: {
        Row: {
          bookmaker_id: number | null
          bookmaker_name: string | null
          created_at: string | null
          external_id: string | null
          id: string
          is_live: boolean | null
          last_updated: string | null
          market_type: string
          match_id: string | null
          odds_data: Json
          odds_timestamp: string
          status: string | null
          updated_at: string | null
        }
        Insert: {
          bookmaker_id?: number | null
          bookmaker_name?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: string
          is_live?: boolean | null
          last_updated?: string | null
          market_type: string
          match_id?: string | null
          odds_data: Json
          odds_timestamp: string
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          bookmaker_id?: number | null
          bookmaker_name?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: string
          is_live?: boolean | null
          last_updated?: string | null
          market_type?: string
          match_id?: string | null
          odds_data?: Json
          odds_timestamp?: string
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_odds_bookmaker_id_fkey"
            columns: ["bookmaker_id"]
            isOneToOne: false
            referencedRelation: "bookmakers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_odds_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      match_predictions: {
        Row: {
          algorithms_used: string[] | null
          away_form: string | null
          away_injuries: Json | null
          away_last_5_goals_conceded: number | null
          away_last_5_goals_scored: number | null
          away_win_probability: number | null
          comparison_stats: Json | null
          confidence_score: number | null
          created_at: string | null
          draw_probability: number | null
          h2h_away_wins: number | null
          h2h_draws: number | null
          h2h_home_wins: number | null
          h2h_last_matches: Json | null
          h2h_total_matches: number | null
          home_form: string | null
          home_injuries: Json | null
          home_last_5_goals_conceded: number | null
          home_last_5_goals_scored: number | null
          home_win_probability: number | null
          id: string
          match_id: string | null
          model_version: string | null
          over_under_predictions: Json | null
          predicted_at: string | null
          predicted_winner: string | null
          updated_at: string | null
        }
        Insert: {
          algorithms_used?: string[] | null
          away_form?: string | null
          away_injuries?: Json | null
          away_last_5_goals_conceded?: number | null
          away_last_5_goals_scored?: number | null
          away_win_probability?: number | null
          comparison_stats?: Json | null
          confidence_score?: number | null
          created_at?: string | null
          draw_probability?: number | null
          h2h_away_wins?: number | null
          h2h_draws?: number | null
          h2h_home_wins?: number | null
          h2h_last_matches?: Json | null
          h2h_total_matches?: number | null
          home_form?: string | null
          home_injuries?: Json | null
          home_last_5_goals_conceded?: number | null
          home_last_5_goals_scored?: number | null
          home_win_probability?: number | null
          id?: string
          match_id?: string | null
          model_version?: string | null
          over_under_predictions?: Json | null
          predicted_at?: string | null
          predicted_winner?: string | null
          updated_at?: string | null
        }
        Update: {
          algorithms_used?: string[] | null
          away_form?: string | null
          away_injuries?: Json | null
          away_last_5_goals_conceded?: number | null
          away_last_5_goals_scored?: number | null
          away_win_probability?: number | null
          comparison_stats?: Json | null
          confidence_score?: number | null
          created_at?: string | null
          draw_probability?: number | null
          h2h_away_wins?: number | null
          h2h_draws?: number | null
          h2h_home_wins?: number | null
          h2h_last_matches?: Json | null
          h2h_total_matches?: number | null
          home_form?: string | null
          home_injuries?: Json | null
          home_last_5_goals_conceded?: number | null
          home_last_5_goals_scored?: number | null
          home_win_probability?: number | null
          id?: string
          match_id?: string | null
          model_version?: string | null
          over_under_predictions?: Json | null
          predicted_at?: string | null
          predicted_winner?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_predictions_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: true
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      match_statistics: {
        Row: {
          awayCorners: number | null
          awayFouls: number | null
          awayPossession: number | null
          awayRedCards: number | null
          awayShotsOnTarget: number | null
          awayTotalShots: number | null
          awayYellowCards: number | null
          createdAt: string
          homeCorners: number | null
          homeFouls: number | null
          homePossession: number | null
          homeRedCards: number | null
          homeShotsOnTarget: number | null
          homeTotalShots: number | null
          homeYellowCards: number | null
          id: string
          matchId: string
          rawData: Json | null
          updatedAt: string
        }
        Insert: {
          awayCorners?: number | null
          awayFouls?: number | null
          awayPossession?: number | null
          awayRedCards?: number | null
          awayShotsOnTarget?: number | null
          awayTotalShots?: number | null
          awayYellowCards?: number | null
          createdAt?: string
          homeCorners?: number | null
          homeFouls?: number | null
          homePossession?: number | null
          homeRedCards?: number | null
          homeShotsOnTarget?: number | null
          homeTotalShots?: number | null
          homeYellowCards?: number | null
          id: string
          matchId: string
          rawData?: Json | null
          updatedAt: string
        }
        Update: {
          awayCorners?: number | null
          awayFouls?: number | null
          awayPossession?: number | null
          awayRedCards?: number | null
          awayShotsOnTarget?: number | null
          awayTotalShots?: number | null
          awayYellowCards?: number | null
          createdAt?: string
          homeCorners?: number | null
          homeFouls?: number | null
          homePossession?: number | null
          homeRedCards?: number | null
          homeShotsOnTarget?: number | null
          homeTotalShots?: number | null
          homeYellowCards?: number | null
          id?: string
          matchId?: string
          rawData?: Json | null
          updatedAt?: string
        }
        Relationships: [
          {
            foreignKeyName: "match_statistics_matchId_fkey"
            columns: ["matchId"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      matches: {
        Row: {
          attendance: number | null
          awayScore: number | null
          awayTeamId: string
          createdAt: string
          externalId: string | null
          halfTimeAway: number | null
          halfTimeHome: number | null
          homeScore: number | null
          homeTeamId: string
          id: string
          lastSyncedAt: string | null
          league_id: string
          matchDate: string
          rawData: Json | null
          referee: string | null
          referee_id: string | null
          round: string | null
          sportId: string
          stadium: string | null
          status: Database["public"]["Enums"]["MatchStatus"]
          updated_at: string
          venue: string | null
          venue_id: string | null
        }
        Insert: {
          attendance?: number | null
          awayScore?: number | null
          awayTeamId: string
          createdAt?: string
          externalId?: string | null
          halfTimeAway?: number | null
          halfTimeHome?: number | null
          homeScore?: number | null
          homeTeamId: string
          id: string
          lastSyncedAt?: string | null
          league_id: string
          matchDate: string
          rawData?: Json | null
          referee?: string | null
          referee_id?: string | null
          round?: string | null
          sportId: string
          stadium?: string | null
          status?: Database["public"]["Enums"]["MatchStatus"]
          updated_at: string
          venue?: string | null
          venue_id?: string | null
        }
        Update: {
          attendance?: number | null
          awayScore?: number | null
          awayTeamId?: string
          createdAt?: string
          externalId?: string | null
          halfTimeAway?: number | null
          halfTimeHome?: number | null
          homeScore?: number | null
          homeTeamId?: string
          id?: string
          lastSyncedAt?: string | null
          league_id?: string
          matchDate?: string
          rawData?: Json | null
          referee?: string | null
          referee_id?: string | null
          round?: string | null
          sportId?: string
          stadium?: string | null
          status?: Database["public"]["Enums"]["MatchStatus"]
          updated_at?: string
          venue?: string | null
          venue_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fk_matches_league_id"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_awayTeamId_fkey"
            columns: ["awayTeamId"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_homeTeamId_fkey"
            columns: ["homeTeamId"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_leagueId_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_referee_id_fkey"
            columns: ["referee_id"]
            isOneToOne: false
            referencedRelation: "referees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_sportId_fkey"
            columns: ["sportId"]
            isOneToOne: false
            referencedRelation: "sports"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_venue_id_fkey"
            columns: ["venue_id"]
            isOneToOne: false
            referencedRelation: "venues"
            referencedColumns: ["id"]
          },
        ]
      }
      odds_movements: {
        Row: {
          bookmaker_name: string | null
          created_at: string | null
          current_odds: Json | null
          id: string
          market_type: string | null
          match_id: string | null
          movement_direction: string | null
          movement_percentage: number | null
          previous_odds: Json | null
          recorded_at: string
        }
        Insert: {
          bookmaker_name?: string | null
          created_at?: string | null
          current_odds?: Json | null
          id?: string
          market_type?: string | null
          match_id?: string | null
          movement_direction?: string | null
          movement_percentage?: number | null
          previous_odds?: Json | null
          recorded_at: string
        }
        Update: {
          bookmaker_name?: string | null
          created_at?: string | null
          current_odds?: Json | null
          id?: string
          market_type?: string | null
          match_id?: string | null
          movement_direction?: string | null
          movement_percentage?: number | null
          previous_odds?: Json | null
          recorded_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "odds_movements_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      performance_metrics: {
        Row: {
          avg_odds: number | null
          calculated_at: string | null
          created_at: string | null
          id: number
          lost_bets: number | null
          net_profit: number | null
          period_end: string
          period_start: string
          period_type: string
          roi_percentage: number | null
          total_bets: number | null
          total_returned: number | null
          total_staked: number | null
          updated_at: string | null
          user_id: string
          void_bets: number | null
          win_rate: number | null
          won_bets: number | null
        }
        Insert: {
          avg_odds?: number | null
          calculated_at?: string | null
          created_at?: string | null
          id?: number
          lost_bets?: number | null
          net_profit?: number | null
          period_end: string
          period_start: string
          period_type: string
          roi_percentage?: number | null
          total_bets?: number | null
          total_returned?: number | null
          total_staked?: number | null
          updated_at?: string | null
          user_id: string
          void_bets?: number | null
          win_rate?: number | null
          won_bets?: number | null
        }
        Update: {
          avg_odds?: number | null
          calculated_at?: string | null
          created_at?: string | null
          id?: number
          lost_bets?: number | null
          net_profit?: number | null
          period_end?: string
          period_start?: string
          period_type?: string
          roi_percentage?: number | null
          total_bets?: number | null
          total_returned?: number | null
          total_staked?: number | null
          updated_at?: string | null
          user_id?: string
          void_bets?: number | null
          win_rate?: number | null
          won_bets?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "performance_metrics_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      player_statistics: {
        Row: {
          created_at: string | null
          external_id: string | null
          id: string
          league_id: string | null
          match_id: string | null
          player_id: string | null
          player_name: string | null
          player_position: string | null
          season_id: string | null
          stat_type: string | null
          statistics: Json
          team_id: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          external_id?: string | null
          id?: string
          league_id?: string | null
          match_id?: string | null
          player_id?: string | null
          player_name?: string | null
          player_position?: string | null
          season_id?: string | null
          stat_type?: string | null
          statistics?: Json
          team_id: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          external_id?: string | null
          id?: string
          league_id?: string | null
          match_id?: string | null
          player_id?: string | null
          player_name?: string | null
          player_position?: string | null
          season_id?: string | null
          stat_type?: string | null
          statistics?: Json
          team_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "player_statistics_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_statistics_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_statistics_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_statistics_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      predictions: {
        Row: {
          confidence: number
          createdAt: string
          id: string
          isCorrect: boolean | null
          matchId: string
          pointsEarned: number
          predictedAwayScore: number | null
          predictedHomeScore: number | null
          predictedOutcome: Database["public"]["Enums"]["PredictionOutcome"]
          reasoning: string | null
          updatedAt: string
          userId: string
        }
        Insert: {
          confidence: number
          createdAt?: string
          id: string
          isCorrect?: boolean | null
          matchId: string
          pointsEarned?: number
          predictedAwayScore?: number | null
          predictedHomeScore?: number | null
          predictedOutcome: Database["public"]["Enums"]["PredictionOutcome"]
          reasoning?: string | null
          updatedAt: string
          userId: string
        }
        Update: {
          confidence?: number
          createdAt?: string
          id?: string
          isCorrect?: boolean | null
          matchId?: string
          pointsEarned?: number
          predictedAwayScore?: number | null
          predictedHomeScore?: number | null
          predictedOutcome?: Database["public"]["Enums"]["PredictionOutcome"]
          reasoning?: string | null
          updatedAt?: string
          userId?: string
        }
        Relationships: [
          {
            foreignKeyName: "predictions_matchId_fkey"
            columns: ["matchId"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "predictions_userId_fkey"
            columns: ["userId"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      referees: {
        Row: {
          birth_date: string | null
          career_start_year: number | null
          country_id: string | null
          created_at: string | null
          external_id: string | null
          fouls_per_match: number | null
          id: string
          is_active: boolean | null
          name: string
          penalties_per_match: number | null
          photo_url: string | null
          red_cards_per_match: number | null
          total_matches: number | null
          updated_at: string | null
          yellow_cards_per_match: number | null
        }
        Insert: {
          birth_date?: string | null
          career_start_year?: number | null
          country_id?: string | null
          created_at?: string | null
          external_id?: string | null
          fouls_per_match?: number | null
          id?: string
          is_active?: boolean | null
          name: string
          penalties_per_match?: number | null
          photo_url?: string | null
          red_cards_per_match?: number | null
          total_matches?: number | null
          updated_at?: string | null
          yellow_cards_per_match?: number | null
        }
        Update: {
          birth_date?: string | null
          career_start_year?: number | null
          country_id?: string | null
          created_at?: string | null
          external_id?: string | null
          fouls_per_match?: number | null
          id?: string
          is_active?: boolean | null
          name?: string
          penalties_per_match?: number | null
          photo_url?: string | null
          red_cards_per_match?: number | null
          total_matches?: number | null
          updated_at?: string | null
          yellow_cards_per_match?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "referees_country_id_fkey"
            columns: ["country_id"]
            isOneToOne: false
            referencedRelation: "countries"
            referencedColumns: ["id"]
          },
        ]
      }
      roi_analysis: {
        Row: {
          calculated_at: string | null
          created_at: string | null
          dimension_type: string
          dimension_value: string
          id: number
          net_profit: number | null
          period_end: string
          period_start: string
          roi_percentage: number | null
          total_bets: number | null
          total_returned: number | null
          total_staked: number | null
          user_id: string
          win_rate: number | null
        }
        Insert: {
          calculated_at?: string | null
          created_at?: string | null
          dimension_type: string
          dimension_value: string
          id?: number
          net_profit?: number | null
          period_end: string
          period_start: string
          roi_percentage?: number | null
          total_bets?: number | null
          total_returned?: number | null
          total_staked?: number | null
          user_id: string
          win_rate?: number | null
        }
        Update: {
          calculated_at?: string | null
          created_at?: string | null
          dimension_type?: string
          dimension_value?: string
          id?: number
          net_profit?: number | null
          period_end?: string
          period_start?: string
          roi_percentage?: number | null
          total_bets?: number | null
          total_returned?: number | null
          total_staked?: number | null
          user_id?: string
          win_rate?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "roi_analysis_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      season_teams: {
        Row: {
          created_at: string
          id: string
          is_active: boolean
          league_id: string
          season_id: string
          team_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id?: string
          is_active?: boolean
          league_id: string
          season_id: string
          team_id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          is_active?: boolean
          league_id?: string
          season_id?: string
          team_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "season_teams_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "season_teams_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "season_teams_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      seasons: {
        Row: {
          created_at: string
          description: string
          end_date: string
          id: string
          is_active: boolean
          start_date: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string
          description: string
          end_date: string
          id?: string
          is_active?: boolean
          start_date: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string
          description?: string
          end_date?: string
          id?: string
          is_active?: boolean
          start_date?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      sports: {
        Row: {
          createdAt: string
          displayOrder: number
          icon: string | null
          id: string
          isActive: boolean
          name: string
          slug: string
          updatedAt: string
        }
        Insert: {
          createdAt?: string
          displayOrder?: number
          icon?: string | null
          id: string
          isActive?: boolean
          name: string
          slug: string
          updatedAt: string
        }
        Update: {
          createdAt?: string
          displayOrder?: number
          icon?: string | null
          id?: string
          isActive?: boolean
          name?: string
          slug?: string
          updatedAt?: string
        }
        Relationships: []
      }
      standings: {
        Row: {
          away_draws: number | null
          away_goals_against: number | null
          away_goals_for: number | null
          away_losses: number | null
          away_matches: number | null
          away_wins: number | null
          created_at: string | null
          draws: number | null
          form: string | null
          goal_difference: number | null
          goals_against: number | null
          goals_for: number | null
          home_draws: number | null
          home_goals_against: number | null
          home_goals_for: number | null
          home_losses: number | null
          home_matches: number | null
          home_wins: number | null
          id: string
          league_id: string | null
          losses: number | null
          matches_played: number | null
          points: number | null
          position: number
          ppg: number | null
          recent_form_points: number | null
          round_number: number | null
          season_id: string | null
          snapshot_date: string
          status: string | null
          team_id: string | null
          updated_at: string | null
          wins: number | null
        }
        Insert: {
          away_draws?: number | null
          away_goals_against?: number | null
          away_goals_for?: number | null
          away_losses?: number | null
          away_matches?: number | null
          away_wins?: number | null
          created_at?: string | null
          draws?: number | null
          form?: string | null
          goal_difference?: number | null
          goals_against?: number | null
          goals_for?: number | null
          home_draws?: number | null
          home_goals_against?: number | null
          home_goals_for?: number | null
          home_losses?: number | null
          home_matches?: number | null
          home_wins?: number | null
          id?: string
          league_id?: string | null
          losses?: number | null
          matches_played?: number | null
          points?: number | null
          position: number
          ppg?: number | null
          recent_form_points?: number | null
          round_number?: number | null
          season_id?: string | null
          snapshot_date: string
          status?: string | null
          team_id?: string | null
          updated_at?: string | null
          wins?: number | null
        }
        Update: {
          away_draws?: number | null
          away_goals_against?: number | null
          away_goals_for?: number | null
          away_losses?: number | null
          away_matches?: number | null
          away_wins?: number | null
          created_at?: string | null
          draws?: number | null
          form?: string | null
          goal_difference?: number | null
          goals_against?: number | null
          goals_for?: number | null
          home_draws?: number | null
          home_goals_against?: number | null
          home_goals_for?: number | null
          home_losses?: number | null
          home_matches?: number | null
          home_wins?: number | null
          id?: string
          league_id?: string | null
          losses?: number | null
          matches_played?: number | null
          points?: number | null
          position?: number
          ppg?: number | null
          recent_form_points?: number | null
          round_number?: number | null
          season_id?: string | null
          snapshot_date?: string
          status?: string | null
          team_id?: string | null
          updated_at?: string | null
          wins?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "standings_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "standings_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      strategy_performance: {
        Row: {
          avg_odds: number | null
          bets_placed: number | null
          bets_won: number | null
          calculated_at: string | null
          created_at: string | null
          id: number
          max_drawdown: number | null
          net_profit: number | null
          period_end: string
          period_start: string
          roi_percentage: number | null
          sharpe_ratio: number | null
          strategy_config: Json | null
          strategy_name: string
          total_returned: number | null
          total_staked: number | null
          user_id: string
          win_rate: number | null
        }
        Insert: {
          avg_odds?: number | null
          bets_placed?: number | null
          bets_won?: number | null
          calculated_at?: string | null
          created_at?: string | null
          id?: number
          max_drawdown?: number | null
          net_profit?: number | null
          period_end: string
          period_start: string
          roi_percentage?: number | null
          sharpe_ratio?: number | null
          strategy_config?: Json | null
          strategy_name: string
          total_returned?: number | null
          total_staked?: number | null
          user_id: string
          win_rate?: number | null
        }
        Update: {
          avg_odds?: number | null
          bets_placed?: number | null
          bets_won?: number | null
          calculated_at?: string | null
          created_at?: string | null
          id?: number
          max_drawdown?: number | null
          net_profit?: number | null
          period_end?: string
          period_start?: string
          roi_percentage?: number | null
          sharpe_ratio?: number | null
          strategy_config?: Json | null
          strategy_name?: string
          total_returned?: number | null
          total_staked?: number | null
          user_id?: string
          win_rate?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "strategy_performance_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      team_injuries: {
        Row: {
          actual_return_date: string | null
          created_at: string | null
          expected_return_date: string | null
          external_id: string | null
          id: string
          injury_description: string | null
          injury_type: string
          matches_missed: number | null
          player_name: string
          player_position: string | null
          severity: string | null
          start_date: string | null
          status: string | null
          team_id: string | null
          updated_at: string | null
        }
        Insert: {
          actual_return_date?: string | null
          created_at?: string | null
          expected_return_date?: string | null
          external_id?: string | null
          id?: string
          injury_description?: string | null
          injury_type: string
          matches_missed?: number | null
          player_name: string
          player_position?: string | null
          severity?: string | null
          start_date?: string | null
          status?: string | null
          team_id?: string | null
          updated_at?: string | null
        }
        Update: {
          actual_return_date?: string | null
          created_at?: string | null
          expected_return_date?: string | null
          external_id?: string | null
          id?: string
          injury_description?: string | null
          injury_type?: string
          matches_missed?: number | null
          player_name?: string
          player_position?: string | null
          severity?: string | null
          start_date?: string | null
          status?: string | null
          team_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_injuries_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      team_statistics: {
        Row: {
          created_at: string | null
          external_id: string | null
          id: string
          league_id: string | null
          match_id: string | null
          season_id: string | null
          stat_type: string | null
          statistics: Json
          team_id: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          external_id?: string | null
          id?: string
          league_id?: string | null
          match_id?: string | null
          season_id?: string | null
          stat_type?: string | null
          statistics?: Json
          team_id: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          external_id?: string | null
          id?: string
          league_id?: string | null
          match_id?: string | null
          season_id?: string | null
          stat_type?: string | null
          statistics?: Json
          team_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_statistics_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_statistics_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_statistics_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_statistics_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      team_stats: {
        Row: {
          avgGoalsConceded: number
          avgGoalsScored: number
          cleanSheets: number
          createdAt: string
          draws: number
          form: string | null
          goalsAgainst: number
          goalsFor: number
          id: string
          losses: number
          matchesPlayed: number
          season: string
          teamId: string
          updatedAt: string
          wins: number
        }
        Insert: {
          avgGoalsConceded?: number
          avgGoalsScored?: number
          cleanSheets?: number
          createdAt?: string
          draws?: number
          form?: string | null
          goalsAgainst?: number
          goalsFor?: number
          id: string
          losses?: number
          matchesPlayed?: number
          season: string
          teamId: string
          updatedAt: string
          wins?: number
        }
        Update: {
          avgGoalsConceded?: number
          avgGoalsScored?: number
          cleanSheets?: number
          createdAt?: string
          draws?: number
          form?: string | null
          goalsAgainst?: number
          goalsFor?: number
          id?: string
          losses?: number
          matchesPlayed?: number
          season?: string
          teamId?: string
          updatedAt?: string
          wins?: number
        }
        Relationships: [
          {
            foreignKeyName: "team_stats_teamId_fkey"
            columns: ["teamId"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      teams: {
        Row: {
          code: string | null
          country_id: string | null
          created_at: string
          external_id: string | null
          founded: number | null
          id: string
          is_active: boolean | null
          logo: string | null
          market_value: number | null
          name: string
          primary_color: string | null
          secondary_color: string | null
          stadium_capacity: number | null
          stadium_name: string | null
          updated_at: string
          website: string | null
        }
        Insert: {
          code?: string | null
          country_id?: string | null
          created_at?: string
          external_id?: string | null
          founded?: number | null
          id: string
          is_active?: boolean | null
          logo?: string | null
          market_value?: number | null
          name: string
          primary_color?: string | null
          secondary_color?: string | null
          stadium_capacity?: number | null
          stadium_name?: string | null
          updated_at: string
          website?: string | null
        }
        Update: {
          code?: string | null
          country_id?: string | null
          created_at?: string
          external_id?: string | null
          founded?: number | null
          id?: string
          is_active?: boolean | null
          logo?: string | null
          market_value?: number | null
          name?: string
          primary_color?: string | null
          secondary_color?: string | null
          stadium_capacity?: number | null
          stadium_name?: string | null
          updated_at?: string
          website?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fk_teams_country_id"
            columns: ["country_id"]
            isOneToOne: false
            referencedRelation: "countries"
            referencedColumns: ["id"]
          },
        ]
      }
      teams_backup_20251029: {
        Row: {
          country: string | null
          country_id: string | null
          createdAt: string | null
          externalId: string | null
          founded: number | null
          id: string | null
          league_id: string | null
          logo: string | null
          name: string | null
          shortName: string | null
          updatedAt: string | null
          venue: string | null
        }
        Insert: {
          country?: string | null
          country_id?: string | null
          createdAt?: string | null
          externalId?: string | null
          founded?: number | null
          id?: string | null
          league_id?: string | null
          logo?: string | null
          name?: string | null
          shortName?: string | null
          updatedAt?: string | null
          venue?: string | null
        }
        Update: {
          country?: string | null
          country_id?: string | null
          createdAt?: string | null
          externalId?: string | null
          founded?: number | null
          id?: string | null
          league_id?: string | null
          logo?: string | null
          name?: string | null
          shortName?: string | null
          updatedAt?: string | null
          venue?: string | null
        }
        Relationships: []
      }
      user_bets: {
        Row: {
          actual_result: string | null
          bet_type: string
          bookmaker_id: number | null
          created_at: string | null
          id: number
          market_id: number
          match_id: string
          notes: string | null
          odds: number
          placed_at: string | null
          potential_return: number | null
          profit_loss: number | null
          selection: string
          settled_at: string | null
          stake: number
          status: string | null
          tip_id: number | null
          updated_at: string | null
          user_id: string
        }
        Insert: {
          actual_result?: string | null
          bet_type: string
          bookmaker_id?: number | null
          created_at?: string | null
          id?: number
          market_id: number
          match_id: string
          notes?: string | null
          odds: number
          placed_at?: string | null
          potential_return?: number | null
          profit_loss?: number | null
          selection: string
          settled_at?: string | null
          stake: number
          status?: string | null
          tip_id?: number | null
          updated_at?: string | null
          user_id: string
        }
        Update: {
          actual_result?: string | null
          bet_type?: string
          bookmaker_id?: number | null
          created_at?: string | null
          id?: number
          market_id?: number
          match_id?: string
          notes?: string | null
          odds?: number
          placed_at?: string | null
          potential_return?: number | null
          profit_loss?: number | null
          selection?: string
          settled_at?: string | null
          stake?: number
          status?: string | null
          tip_id?: number | null
          updated_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_bets_bookmaker_id_fkey"
            columns: ["bookmaker_id"]
            isOneToOne: false
            referencedRelation: "bookmakers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_bets_market_id_fkey"
            columns: ["market_id"]
            isOneToOne: false
            referencedRelation: "betting_markets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_bets_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_bets_tip_id_fkey"
            columns: ["tip_id"]
            isOneToOne: false
            referencedRelation: "betting_tips"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_bets_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      user_settings: {
        Row: {
          createdAt: string
          emailNotifications: boolean
          favoriteLeagues: string[] | null
          favoriteSports: string[] | null
          id: string
          language: string
          notificationsEnabled: boolean
          theme: string
          updatedAt: string
          userId: string
        }
        Insert: {
          createdAt?: string
          emailNotifications?: boolean
          favoriteLeagues?: string[] | null
          favoriteSports?: string[] | null
          id: string
          language?: string
          notificationsEnabled?: boolean
          theme?: string
          updatedAt: string
          userId: string
        }
        Update: {
          createdAt?: string
          emailNotifications?: boolean
          favoriteLeagues?: string[] | null
          favoriteSports?: string[] | null
          id?: string
          language?: string
          notificationsEnabled?: boolean
          theme?: string
          updatedAt?: string
          userId?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_settings_userId_fkey"
            columns: ["userId"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      user_stats: {
        Row: {
          accuracy: number
          correctPredictions: number
          createdAt: string
          currentStreak: number
          id: string
          longestStreak: number
          totalPoints: number
          totalPredictions: number
          updatedAt: string
          userId: string
        }
        Insert: {
          accuracy?: number
          correctPredictions?: number
          createdAt?: string
          currentStreak?: number
          id: string
          longestStreak?: number
          totalPoints?: number
          totalPredictions?: number
          updatedAt: string
          userId: string
        }
        Update: {
          accuracy?: number
          correctPredictions?: number
          createdAt?: string
          currentStreak?: number
          id?: string
          longestStreak?: number
          totalPoints?: number
          totalPredictions?: number
          updatedAt?: string
          userId?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_stats_userId_fkey"
            columns: ["userId"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      users: {
        Row: {
          avatarUrl: string | null
          createdAt: string
          email: string
          emailVerified: boolean
          fullName: string | null
          id: string
          isActive: boolean
          lastLoginAt: string | null
          role: Database["public"]["Enums"]["UserRole"]
          updatedAt: string
          username: string | null
        }
        Insert: {
          avatarUrl?: string | null
          createdAt?: string
          email: string
          emailVerified?: boolean
          fullName?: string | null
          id: string
          isActive?: boolean
          lastLoginAt?: string | null
          role?: Database["public"]["Enums"]["UserRole"]
          updatedAt: string
          username?: string | null
        }
        Update: {
          avatarUrl?: string | null
          createdAt?: string
          email?: string
          emailVerified?: boolean
          fullName?: string | null
          id?: string
          isActive?: boolean
          lastLoginAt?: string | null
          role?: Database["public"]["Enums"]["UserRole"]
          updatedAt?: string
          username?: string | null
        }
        Relationships: []
      }
      value_bet_identification: {
        Row: {
          bookmaker_id: number | null
          bookmaker_odds: number
          confidence_score: number | null
          created_at: string | null
          expected_value: number
          expires_at: string | null
          fair_odds: number
          id: number
          identified_at: string | null
          kelly_criterion: number | null
          market_id: number
          match_id: string
          predicted_probability: number
          selection: string
          status: string | null
          updated_at: string | null
          value_percentage: number
        }
        Insert: {
          bookmaker_id?: number | null
          bookmaker_odds: number
          confidence_score?: number | null
          created_at?: string | null
          expected_value: number
          expires_at?: string | null
          fair_odds: number
          id?: number
          identified_at?: string | null
          kelly_criterion?: number | null
          market_id: number
          match_id: string
          predicted_probability: number
          selection: string
          status?: string | null
          updated_at?: string | null
          value_percentage: number
        }
        Update: {
          bookmaker_id?: number | null
          bookmaker_odds?: number
          confidence_score?: number | null
          created_at?: string | null
          expected_value?: number
          expires_at?: string | null
          fair_odds?: number
          id?: number
          identified_at?: string | null
          kelly_criterion?: number | null
          market_id?: number
          match_id?: string
          predicted_probability?: number
          selection?: string
          status?: string | null
          updated_at?: string | null
          value_percentage?: number
        }
        Relationships: [
          {
            foreignKeyName: "value_bet_identification_bookmaker_id_fkey"
            columns: ["bookmaker_id"]
            isOneToOne: false
            referencedRelation: "bookmakers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "value_bet_identification_market_id_fkey"
            columns: ["market_id"]
            isOneToOne: false
            referencedRelation: "betting_markets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "value_bet_identification_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      venues: {
        Row: {
          address: string | null
          capacity: number | null
          city: string | null
          country_id: string | null
          created_at: string | null
          external_id: string | null
          id: string
          is_active: boolean | null
          latitude: number | null
          longitude: number | null
          name: string
          opened_year: number | null
          photo_url: string | null
          roof_type: string | null
          surface: string | null
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          capacity?: number | null
          city?: string | null
          country_id?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: string
          is_active?: boolean | null
          latitude?: number | null
          longitude?: number | null
          name: string
          opened_year?: number | null
          photo_url?: string | null
          roof_type?: string | null
          surface?: string | null
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          capacity?: number | null
          city?: string | null
          country_id?: string | null
          created_at?: string | null
          external_id?: string | null
          id?: string
          is_active?: boolean | null
          latitude?: number | null
          longitude?: number | null
          name?: string
          opened_year?: number | null
          photo_url?: string | null
          roof_type?: string | null
          surface?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "venues_country_id_fkey"
            columns: ["country_id"]
            isOneToOne: false
            referencedRelation: "countries"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      MatchStatus: "SCHEDULED" | "LIVE" | "FINISHED" | "POSTPONED" | "CANCELLED"
      PredictionOutcome: "HOME_WIN" | "DRAW" | "AWAY_WIN"
      UserRole: "USER" | "PREMIUM" | "ADMIN"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      MatchStatus: ["SCHEDULED", "LIVE", "FINISHED", "POSTPONED", "CANCELLED"],
      PredictionOutcome: ["HOME_WIN", "DRAW", "AWAY_WIN"],
      UserRole: ["USER", "PREMIUM", "ADMIN"],
    },
  },
} as const
