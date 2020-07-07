#!/usr/bin/python
# -*- coding:utf-8 -*-
"""question-answering system"""
from math import sqrt
from collections import defaultdict

class QuestionAnswering:
    """class of QA"""
    def __init__(self, database):
        """database: database of all tagged messages"""
        self.database = database

    @classmethod
    def get_tags_from_msg(cls, text: str):
        """split text and get tags"""
        return text

    @classmethod
    def cosine_similarity(cls, text1, text2):
        """compare the cosine similarity between two texts"""

        # count frequency of characters
        counter1 = defaultdict(lambda: 0)
        counter2 = defaultdict(lambda: 0)
        for char in text1:
            counter1[char] += 1
        for char in text2:
            counter2[char] += 1

        # vectorize and dot
        all_char = set(list(counter1.keys()) + list(counter2.keys()))
        len1_sqr = 0
        len2_sqr = 0
        dot = 0 # dot result of two vectors
        for char in all_char:
            dot += counter1[char] * counter2[char]
            len1_sqr += counter1[char] * counter1[char]
            len2_sqr += counter2[char] * counter2[char]

        # cosine similarity
        return dot / sqrt(len1_sqr * len2_sqr)

    def cmp_tags(self, text1, text2):
        """decide whether the two tags are matched"""
        return self.cosine_similarity(text1, text2) > 0.5
