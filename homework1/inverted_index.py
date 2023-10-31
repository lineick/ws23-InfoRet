from typing import List, Tuple, Dict
import re


class InvertedIndex:
    def __init__(self):
        self.dictionary = {}
        self.postings_lists = {}
        self.postings_list_id_counter = 0

    def normalize_term(self, term: str) -> str:
        """
        Normalize the term by converting it to lowercase and removing any non-alphanumeric characters.
        """
        return re.sub(r"\W+", "", term.lower())

    def index(self, filename: str):
        """
        Index the documents in the given file.
        """
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                columns = line.strip().split("\t")
                if len(columns) < 5:
                    continue
                tweet_id = columns[1]
                tweet_text = columns[4]
                terms = tweet_text.split()
                unique_terms = set()
                for term in terms:
                    normalized_term = self.normalize_term(term)
                    if normalized_term and normalized_term not in unique_terms:
                        unique_terms.add(normalized_term)
                        if normalized_term not in self.dictionary:
                            postings_list_id = self.postings_list_id_counter
                            self.postings_lists[postings_list_id] = []
                            self.dictionary[normalized_term] = (0, postings_list_id)
                            self.postings_list_id_counter += 1
                        size, postings_list_id = self.dictionary[normalized_term]
                        postings_list = self.postings_lists[postings_list_id]
                        if not postings_list or postings_list[-1][0] != tweet_id:
                            postings_list.append((tweet_id, None))
                            self.dictionary[normalized_term] = (
                                size + 1,
                                postings_list_id,
                            )
                            if len(postings_list) > 1:
                                postings_list[-2] = (
                                    postings_list[-2][0],
                                    len(postings_list) - 1,
                                )

    def query(self, term: str) -> List[Tuple[str, int]]:
        """
        Query the index for a single term and return the postings list.
        """
        normalized_term = self.normalize_term(term)
        if normalized_term in self.dictionary:
            size, postings_list_id = self.dictionary[normalized_term]
            return self.postings_lists[postings_list_id]
        return []


class InvertedIndex(InvertedIndex):
    def intersect_postings_lists(
        self,
        postings_list1: List[Tuple[str, int]],
        postings_list2: List[Tuple[str, int]],
    ) -> List[str]:
        """
        Intersect two postings lists and return the common document IDs.
        """
        result = []
        iter1 = iter(postings_list1)
        iter2 = iter(postings_list2)
        posting1 = next(iter1, None)
        posting2 = next(iter2, None)
        while posting1 is not None and posting2 is not None:
            doc_id1, next_posting1 = posting1
            doc_id2, next_posting2 = posting2
            if doc_id1 == doc_id2:
                result.append(doc_id1)
                posting1 = next(iter1, None) if next_posting1 is not None else None
                posting2 = next(iter2, None) if next_posting2 is not None else None
            elif doc_id1 < doc_id2:
                posting1 = next(iter1, None) if next_posting1 is not None else None
            else:
                posting2 = next(iter2, None) if next_posting2 is not None else None
        return result

    def query(self, term1: str, term2: str = None) -> List[str]:
        """
        Query the index for one or two terms and return the document IDs.
        """
        postings_list1 = super().query(term1)
        if term2 is not None:
            postings_list2 = super().query(term2)
            return self.intersect_postings_lists(postings_list1, postings_list2)
        return [doc_id for doc_id, _ in postings_list1]


# Test the query method
index = InvertedIndex()
index.index("./homework1/tweets.csv")
index.query("cancer", "vaccine")
