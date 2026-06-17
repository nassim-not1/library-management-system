import math
import re
import unicodedata
from collections import Counter


class RecommendationService:
    CONTENT_FIELDS = ("titre", "auteur", "categorie", "description", "mots_cles")

    def _load_sklearn(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            return None, None

        return TfidfVectorizer, cosine_similarity

    def _build_document(self, livre):
        parts = []
        for field in self.CONTENT_FIELDS:
            value = str(livre.get(field, "")).strip()
            if value:
                parts.append(value)

        mots_cles = str(livre.get("mots_cles", "")).strip()
        if mots_cles:
            parts.extend([mots_cles, mots_cles])

        return " ".join(parts)

    def _tokenize(self, document):
        normalized = unicodedata.normalize("NFKD", document.lower())
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        return re.findall(r"[a-z0-9]+", normalized)

    def _fallback_similarity_scores(self, documents, target_index):
        tokenized_documents = [self._tokenize(document) for document in documents]
        document_count = len(tokenized_documents)
        document_frequency = Counter()

        for tokens in tokenized_documents:
            document_frequency.update(set(tokens))

        vectors = []
        for tokens in tokenized_documents:
            token_counts = Counter(tokens)
            total_tokens = sum(token_counts.values()) or 1
            vector = {}

            for token, count in token_counts.items():
                tf = count / total_tokens
                idf = math.log((1 + document_count) / (1 + document_frequency[token])) + 1
                vector[token] = tf * idf

            vectors.append(vector)

        target_vector = vectors[target_index]
        target_norm = math.sqrt(sum(value * value for value in target_vector.values()))
        scores = []

        for vector in vectors:
            vector_norm = math.sqrt(sum(value * value for value in vector.values()))
            if not target_norm or not vector_norm:
                scores.append(0)
                continue

            common_tokens = set(target_vector) & set(vector)
            dot_product = sum(target_vector[token] * vector[token] for token in common_tokens)
            scores.append(dot_product / (target_norm * vector_norm))

        return scores

    def recommend_by_book(self, livres, id_livre, top_n=5):
        if not livres or len(livres) < 2:
            return []

        target_id = str(id_livre)
        target_index = next(
            (index for index, livre in enumerate(livres) if str(livre.get("id_livre", "")) == target_id),
            None,
        )

        if target_index is None:
            raise ValueError("Livre introuvable pour la recommandation.")

        documents = [self._build_document(livre) for livre in livres]
        TfidfVectorizer, cosine_similarity = self._load_sklearn()

        if TfidfVectorizer and cosine_similarity:
            vectorizer = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(documents)
            similarity_scores = cosine_similarity(tfidf_matrix[target_index], tfidf_matrix).flatten()
        else:
            similarity_scores = self._fallback_similarity_scores(documents, target_index)

        ranked_candidates = sorted(
            (
                (index, score)
                for index, score in enumerate(similarity_scores)
                if index != target_index and score > 0
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        recommendations = []
        for index, score in ranked_candidates[:top_n]:
            livre = livres[index].copy()
            livre["score_recommandation"] = f"{round(float(score) * 100)}%"
            recommendations.append(livre)

        return recommendations
