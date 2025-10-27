import { PrismaClient } from '@prisma/client';

/**
 * Prisma Client Singleton
 * 
 * Prevents multiple instances in development (hot reload)
 * Uses connection pooling for better performance
 */

// Extend global type to include prisma
declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Create Prisma Client with appropriate logging
export const prisma =
  global.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' 
      ? ['query', 'error', 'warn'] 
      : ['error'],
  });

// In development, attach to global to prevent multiple instances
if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

/**
 * Graceful shutdown handler
 * Ensures database connections are properly closed
 */
process.on('beforeExit', async () => {
  await prisma.$disconnect();
});

export default prisma;