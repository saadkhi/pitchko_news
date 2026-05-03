import { NextResponse } from 'next/server'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function GET() {
  try {
    const breakingNews = await prisma.news.findMany({
      where: {
        impactLevel: {
          in: ['high', 'critical']
        },
        credibilityScore: {
          gt: 0.9
        }
      },
      orderBy: { publishedAt: 'desc' },
      take: 10,
      include: {
        videos: true
      }
    })

    return NextResponse.json(breakingNews)
  } catch (error) {
    console.error('Error fetching breaking news:', error)
    return NextResponse.json(
      { error: 'Failed to fetch breaking news' },
      { status: 500 }
    )
  }
}
