import os
import httpx
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()


class GitHubClassroomClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_CLASSROOM_TOKEN")
        if not self.token:
            raise ValueError("GitHub token not provided")
        self.headers = {
            "Authorization": f"bearer {self.token}",
            "Accept": "application/vnd.github.v4+json"
        }
        self.keys_for_assignments = ['id', 'title', 'submissions', 'deadline', 'classroom']
        self.keys_for_submissions = ['id', 'submitted', 'grade', ]

    async def get_courses(self):
        """
        Вернуть все курсы, доступные по токену клиента
        :return: json формата: {"id": id,
                                "name": name,
                                "archived": archived,
                                "url": url}
        """
        with httpx.Client() as client:
            resp = client.get("https://api.github.com/classrooms", headers=self.headers)
            resp.raise_for_status()
            classrooms = resp.json()
        return classrooms

    async def get_course_details(self, course_id: int):
        """
        Вернуть все детали курса
        :param course_id айди курса
        :return: json формата: {"id": id,
                                "name": name,
                                "archived": archived,
                                "url": url,
                                "organization": organization}
        """
        url = f"https://api.github.com/classrooms/{course_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            course_details = resp.json()
        return course_details

    async def get_assignments(self, classroom_id: int):
        """
        Вернуть все задания из классрума по айди
        :param classroom_id: id классрума в гитхабе
        :return: json формата: {"id": id,
                                "title": title,
                                "submissions": submissions,
                                "deadline": deadline
                                "classroom": classroom
                                }
        """
        with httpx.Client() as client:
            resp = client.get(
                f"https://api.github.com/classrooms/{classroom_id}/assignments",
                headers=self.headers,
            )
            resp.raise_for_status()
            assignments = resp.json()
        assignments_filtered = []
        for assignment in assignments:
            assignments_filtered.append({key: assignment[key] for key in self.keys_for_assignments})
        return assignments_filtered

    async def get_submissions(self, assignment_id: int):
        """
        Вернуть все сдачи определенного задания
        :param assignment_id: id задания в гитхабе
        :return: json формата: {"id": id,
                                "title": title,
                                "submissions": submissions,
                                "deadline": deadline
                                "classroom": classroom
                                }
        """
        with httpx.Client() as client:
            resp = client.get(
                f"https://api.github.com/assignments/{assignment_id}/accepted_assignments",
                headers=self.headers,
            )
            resp.raise_for_status()
            submissions = resp.json()
        return submissions

    async def test_connection(self) -> bool:
        try:
            await self.get_courses()
            return True
        except Exception:
            return False


async def main():
    gh = GitHubClassroomClient()
    courses = await gh.get_courses()
    for course in courses:
        print("course: ", course)
        assignments = await gh.get_assignments(course["id"])
        details = await gh.get_course_details(course["id"])
        print("details:", details)
        for assignment in assignments:
            print("assignment: ", assignment)
            submissions = await gh.get_submissions(assignment["id"])
            for submission in submissions:
                print("submission: ", submission)


if __name__ == "__main__":
    asyncio.run(main())
