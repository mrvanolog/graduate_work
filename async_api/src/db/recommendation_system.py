from typing import Optional
import requests


class RecommendationSystem:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def __build_url__(self, endpoint: str):
        return f'{self.base_url}/{endpoint}'

    def get(self, endpoint: str, params: Optional[dict] = None):
        if params is None:
            params = {}
        url = self.__build_url__(endpoint)
        response = requests.get(url, params)
        return response

    def get_recommendations_for_user(self, user_id: str) -> dict:
        endpoint = 'v1/predictions/user'
        params = {'user_id': user_id}
        response = self.get(endpoint, params=params)
        data = response.json()
        return data

    def get_recommendations_for_movie(self, movie_id: str) -> dict:
        endpoint = 'v1/predictions/movie'
        params = {'movie_id': movie_id}
        response = self.get(endpoint, params=params)
        data = response.json()
        return data