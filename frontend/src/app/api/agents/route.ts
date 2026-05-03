import { NextResponse } from 'next/server'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function POST() {
  try {
    // Mock agent pipeline trigger
    const agentRun = await prisma.agentRun.create({
      data: {
        agentType: 'orchestrator',
        status: 'running',
        startedAt: new Date()
      }
    })

    // Simulate async processing
    setTimeout(async () => {
      await prisma.agentRun.update({
        where: { id: agentRun.id },
        data: {
          status: 'completed',
          completedAt: new Date(),
          result: JSON.stringify({
            newsProcessed: 15,
            trendsUpdated: 5,
            videosGenerated: 2
          })
        }
      })
    }, 5000)

    return NextResponse.json({ 
      message: 'Agent pipeline triggered successfully',
      runId: agentRun.id
    })
  } catch (error) {
    console.error('Error triggering agents:', error)
    return NextResponse.json(
      { error: 'Failed to trigger agents' },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    const runs = await prisma.agentRun.findMany({
      orderBy: { startedAt: 'desc' },
      take: 10
    })

    return NextResponse.json(runs)
  } catch (error) {
    console.error('Error fetching agent runs:', error)
    return NextResponse.json(
      { error: 'Failed to fetch agent runs' },
      { status: 500 }
    )
  }
}
