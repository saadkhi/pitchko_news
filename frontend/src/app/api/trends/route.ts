import { NextResponse } from 'next/server'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function GET() {
  try {
    const trends = await prisma.trend.findMany({
      orderBy: { count: 'desc' },
      take: 20
    })

    return NextResponse.json(trends)
  } catch (error) {
    console.error('Error fetching trends:', error)
    return NextResponse.json(
      { error: 'Failed to fetch trends' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const trend = await prisma.trend.create({
      data: {
        ...body,
        lastUpdated: new Date()
      }
    })

    return NextResponse.json(trend, { status: 201 })
  } catch (error) {
    console.error('Error creating trend:', error)
    return NextResponse.json(
      { error: 'Failed to create trend' },
      { status: 500 }
    )
  }
}
