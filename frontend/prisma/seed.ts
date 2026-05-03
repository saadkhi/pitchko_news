import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  // Create sample news articles
  const news1 = await prisma.news.create({
    data: {
      title: 'AI Breakthrough: New Model Achieves Human-Level Performance',
      summary: 'Latest AI research shows significant improvements in natural language understanding and reasoning capabilities.',
      content: 'Researchers have developed a new AI model that demonstrates unprecedented performance in complex reasoning tasks...',
      category: 'AI/ML',
      impactLevel: 'high',
      credibilityScore: 0.95,
      publishedAt: new Date('2024-01-15T10:00:00Z'),
      url: 'https://example.com/ai-breakthrough',
      imageUrl: 'https://example.com/ai-image.jpg',
      source: 'Tech Research Institute',
      tags: JSON.stringify(['ai', 'machine-learning', 'breakthrough', 'research'])
    }
  })

  const news2 = await prisma.news.create({
    data: {
      title: 'Tech Giants Announce Cloud Computing Partnership',
      summary: 'Major technology companies collaborate on next-generation cloud infrastructure to improve scalability and performance.',
      content: 'In a landmark announcement today, leading tech companies revealed a strategic partnership to develop next-generation cloud computing infrastructure...',
      category: 'Cloud',
      impactLevel: 'medium',
      credibilityScore: 0.88,
      publishedAt: new Date('2024-01-15T09:30:00Z'),
      url: 'https://example.com/cloud-partnership',
      imageUrl: 'https://example.com/cloud-image.jpg',
      source: 'Business News Daily',
      tags: JSON.stringify(['cloud', 'partnership', 'infrastructure', 'tech-giants'])
    }
  })

  const news3 = await prisma.news.create({
    data: {
      title: 'Cybersecurity Threat Alert: New Vulnerability Discovered',
      summary: 'Security researchers identify critical vulnerability affecting millions of devices worldwide.',
      content: 'A critical security vulnerability has been discovered that affects millions of devices across various platforms...',
      category: 'Security',
      impactLevel: 'critical',
      credibilityScore: 0.92,
      publishedAt: new Date('2024-01-15T08:45:00Z'),
      url: 'https://example.com/security-alert',
      imageUrl: 'https://example.com/security-image.jpg',
      source: 'Cybersecurity Weekly',
      tags: JSON.stringify(['security', 'vulnerability', 'cybersecurity', 'alert'])
    }
  })

  // Create trends
  await prisma.trend.createMany({
    data: [
      { topic: 'Artificial Intelligence', count: 45, sentiment: 'positive' },
      { topic: 'Cloud Computing', count: 32, sentiment: 'neutral' },
      { topic: 'Cybersecurity', count: 28, sentiment: 'positive' },
      { topic: 'Blockchain', count: 15, sentiment: 'neutral' },
      { topic: 'Quantum Computing', count: 12, sentiment: 'positive' }
    ]
  })

  // Create sample video
  await prisma.video.create({
    data: {
      title: 'AI Weekly Roundup',
      description: 'Latest developments in artificial intelligence and machine learning',
      url: 'https://example.com/video1',
      thumbnailUrl: 'https://example.com/thumb1.jpg',
      duration: '5:30',
      status: 'ready',
      newsId: news1.id
    }
  })

  console.log('Database seeded successfully!')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    await prisma.$disconnect()
    process.exit(1)
  })
