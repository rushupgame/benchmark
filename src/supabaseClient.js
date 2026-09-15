import { createClient } from '@supabase/supabase-js'

// Remplace par tes vraies clés Supabase (Project Settings > API)
const supabaseUrl = 'https://drscbjrshjhupvrrzqec.supabase.co'
const supabaseAnonKey = 'sb_publishable_E4VeSUjg8eD2KxN9fzrkmg_D_sVfHDV'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)