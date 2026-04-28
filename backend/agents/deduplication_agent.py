from typing import Dict, Any, List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import logging
from .base_agent import BaseAgent

class DeduplicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("DeduplicationAgent")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.8
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate or similar articles using embeddings"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "duplicates_removed": 0}
            
            # Generate embeddings for all articles
            embeddings = await self.generate_embeddings(articles)
            
            # Find similar articles
            duplicate_groups = self.find_similar_articles(articles, embeddings)
            
            # Merge duplicate groups
            deduplicated_articles = self.merge_duplicate_groups(articles, duplicate_groups)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": deduplicated_articles,
                "original_count": len(articles),
                "duplicates_removed": len(articles) - len(deduplicated_articles),
                "duplicate_groups": len(duplicate_groups)
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Deduplication failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def generate_embeddings(self, articles: List[Dict[str, Any]]) -> np.ndarray:
        """Generate embeddings for article titles and content"""
        texts = []
        for article in articles:
            # Combine title and content for better similarity detection
            title = article.get("title", "")
            content = article.get("content", "")[:500]  # Limit content length
            combined_text = f"{title} {content}"
            texts.append(combined_text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings
    
    def find_similar_articles(self, articles: List[Dict[str, Any]], embeddings: np.ndarray) -> List[List[int]]:
        """Find groups of similar articles using cosine similarity"""
        similarity_matrix = cosine_similarity(embeddings)
        
        # Find similar pairs
        similar_pairs = []
        n = len(articles)
        
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] > self.similarity_threshold:
                    similar_pairs.append((i, j, similarity_matrix[i][j]))
        
        # Group similar articles
        duplicate_groups = self.group_similar_articles(similar_pairs, n)
        
        return duplicate_groups
    
    def group_similar_articles(self, similar_pairs: List[Tuple[int, int, float]], n: int) -> List[List[int]]:
        """Group similar articles using union-find"""
        parent = list(range(n))
        rank = [0] * n
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return
            if rank[px] < rank[py]:
                parent[px] = py
            elif rank[px] > rank[py]:
                parent[py] = px
            else:
                parent[py] = px
                rank[px] += 1
        
        # Union similar pairs
        for i, j, similarity in similar_pairs:
            union(i, j)
        
        # Group by parent
        groups = {}
        for i in range(n):
            parent_i = find(i)
            if parent_i not in groups:
                groups[parent_i] = []
            groups[parent_i].append(i)
        
        # Return only groups with more than 1 article
        return [group for group in groups.values() if len(group) > 1]
    
    def merge_duplicate_groups(self, articles: List[Dict[str, Any]], duplicate_groups: List[List[int]]) -> List[Dict[str, Any]]:
        """Merge duplicate groups into single articles"""
        if not duplicate_groups:
            return articles
        
        # Track indices to remove
        indices_to_remove = set()
        merged_articles = []
        
        for group in duplicate_groups:
            # Sort by trust score and publication date
            group_articles = [articles[i] for i in group]
            group_articles.sort(key=lambda x: (
                -x.get("trust_score", 0.5),
                x.get("published_at", datetime.min)
            ))
            
            # Keep the best article as the main one
            main_article = group_articles[0]
            other_articles = group_articles[1:]
            
            # Merge information from other articles
            merged_article = self.merge_articles(main_article, other_articles)
            
            # Mark other indices for removal
            for i in group[1:]:
                indices_to_remove.add(i)
            
            merged_articles.append(merged_article)
        
        # Keep articles that are not duplicates
        deduplicated_articles = []
        for i, article in enumerate(articles):
            if i not in indices_to_remove:
                # Check if this article was merged
                merged_version = next((ma for ma in merged_articles if ma.get("original_index") == i), None)
                if merged_version:
                    deduplicated_articles.append(merged_version)
                else:
                    article["original_index"] = i
                    deduplicated_articles.append(article)
        
        return deduplicated_articles
    
    def merge_articles(self, main_article: Dict[str, Any], other_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge information from duplicate articles"""
        merged = main_article.copy()
        
        # Combine sources
        all_sources = [main_article.get("source_name", "")]
        for article in other_articles:
            source_name = article.get("source_name", "")
            if source_name and source_name not in all_sources:
                all_sources.append(source_name)
        
        # Update source count and trust score
        merged["source_count"] = len(all_sources)
        merged["all_sources"] = all_sources
        
        # Average trust scores
        trust_scores = [main_article.get("trust_score", 0.5)]
        for article in other_articles:
            trust_scores.append(article.get("trust_score", 0.5))
        merged["trust_score"] = np.mean(trust_scores)
        
        # Combine content (keep main content, add references)
        merged["additional_sources"] = []
        for article in other_articles:
            if article.get("url") != main_article.get("url"):
                merged["additional_sources"].append({
                    "url": article.get("url"),
                    "source_name": article.get("source_name"),
                    "title": article.get("title")
                })
        
        # Store original index for tracking
        merged["original_index"] = articles.index(main_article) if main_article in articles else 0
        
        return merged
