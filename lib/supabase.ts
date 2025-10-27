import { createClient } from '@supabase/supabase-js';

/**
 * Environment Variables Validation
 * Ensures required Supabase credentials are present
 */
if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_URL');
}
if (!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY');
}

/**
 * Supabase Client (Public)
 * 
 * Used for:
 * - Authentication (sign up, sign in, sign out)
 * - Storage (file uploads)
 * - Real-time subscriptions
 * 
 * This client uses the anon/public key and respects RLS policies
 */
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
    },
  }
);

/**
 * Supabase Admin Client (Server-side only)
 * 
 * Used for:
 * - Server-side operations that bypass RLS
 * - Admin tasks
 * - Background jobs
 * 
 * NEVER expose this client to the frontend!
 */
export const getServiceSupabase = () => {
  if (!process.env.SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error('Missing env.SUPABASE_SERVICE_ROLE_KEY');
  }

  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    }
  );
};

/**
 * Helper: Get current user session
 */
export async function getCurrentUser() {
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error) {
    console.error('Error getting session:', error);
    return null;
  }
  
  return session?.user ?? null;
}

/**
 * Helper: Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const user = await getCurrentUser();
  return !!user;
}

export default supabase;