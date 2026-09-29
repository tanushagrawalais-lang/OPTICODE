-- ============================================================
-- OptiCode Backend A — Initial Database Schema & RLS Policies
-- ============================================================
-- Migration: 20260929000000_initial_schema.sql
-- Description: Creates users, conversations, and messages tables
--              with constraints, indexes, timestamps, and Row Level Security.
-- ============================================================

-- Ensure pgcrypto or uuid extension is available for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
-- Mirrors authenticated users. In production Supabase, references auth.users(id).
-- Can also be used standalone for local testing environments.
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.users IS 'Application user profile records linked to Supabase Auth.';

-- ============================================================
-- 2. CONVERSATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.conversations IS 'Conversations owned by users in the OptiCode workspace.';

-- Indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON public.conversations (user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON public.conversations (updated_at DESC);

-- ============================================================
-- 3. MESSAGES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.messages IS 'Messages within a conversation (user prompts, AI responses, system notices).';

-- Indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON public.messages (conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_chronological
    ON public.messages (conversation_id, created_at ASC);

-- ============================================================
-- 4. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------
-- USERS POLICIES
-- ------------------------------------------------------------
-- Users can view their own record
CREATE POLICY "Users can view own profile"
    ON public.users
    FOR SELECT
    USING (auth.uid() = id);

-- Users can insert their own record upon registration
CREATE POLICY "Users can insert own profile"
    ON public.users
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Users can update their own record
CREATE POLICY "Users can update own profile"
    ON public.users
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- ------------------------------------------------------------
-- CONVERSATIONS POLICIES
-- ------------------------------------------------------------
-- Users can only select their own conversations
CREATE POLICY "Users can select own conversations"
    ON public.conversations
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only create conversations for themselves
CREATE POLICY "Users can insert own conversations"
    ON public.conversations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own conversations
CREATE POLICY "Users can update own conversations"
    ON public.conversations
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can only delete their own conversations
CREATE POLICY "Users can delete own conversations"
    ON public.conversations
    FOR DELETE
    USING (auth.uid() = user_id);

-- ------------------------------------------------------------
-- MESSAGES POLICIES
-- ------------------------------------------------------------
-- Messages are accessible only if the user owns the parent conversation
CREATE POLICY "Users can select messages in own conversations"
    ON public.messages
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.conversations
            WHERE public.conversations.id = public.messages.conversation_id
              AND public.conversations.user_id = auth.uid()
        )
    );

-- Messages can only be added to conversations owned by the user
CREATE POLICY "Users can insert messages into own conversations"
    ON public.messages
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.conversations
            WHERE public.conversations.id = public.messages.conversation_id
              AND public.conversations.user_id = auth.uid()
        )
    );

-- Messages can only be updated if user owns the parent conversation
CREATE POLICY "Users can update messages in own conversations"
    ON public.messages
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.conversations
            WHERE public.conversations.id = public.messages.conversation_id
              AND public.conversations.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.conversations
            WHERE public.conversations.id = public.messages.conversation_id
              AND public.conversations.user_id = auth.uid()
        )
    );

-- Messages can only be deleted if user owns the parent conversation
CREATE POLICY "Users can delete messages in own conversations"
    ON public.messages
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.conversations
            WHERE public.conversations.id = public.messages.conversation_id
              AND public.conversations.user_id = auth.uid()
        )
    );
