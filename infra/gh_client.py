import os
import httpx
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import asyncio

load_dotenv()


class GitHubClassroomClient:
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_CLASSROOM_TOKEN")
        if not self.token:
            raise ValueError("GitHub token not provided")
        self.headers = {
            "Authorization": f"bearer {self.token}",
            "Accept": "application/vnd.github.v4+json"
        }

    async def get_orgs(self):
        """Получить список организаций пользователя"""
        query = """
        query {
          viewer {
            organizations(first: 100) {
              nodes {
                login
              }
            }
          }
        }
        """

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.GRAPHQL_URL, headers=self.headers, json={"query": query})
            resp.raise_for_status()
            data = resp.json()

        res = [org["login"] for org in data["data"]["viewer"]["organizations"]["nodes"]]
        print(res)
        return res

    async def get_assignments_from_org(self, org_login: str):
        """Получить задания (репозитории) организации"""
        query = """
        query($org: String!) {
          organization(login: $org) {
            repositories(first: 100) {
              nodes {
                name
                url
              }
              
            }
          }
        }
        """

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.GRAPHQL_URL,
                headers=self.headers,
                json={"query": query, "variables": {"org": org_login}}
            )
            resp.raise_for_status()
            data = resp.json()

        repos = data["data"]["organization"]["repositories"]["nodes"]
        return [{"name": r["name"], "url": r["url"]} for r in repos]

    async def get_students_from_org(self, org_login: str):
        """Получить список студентов (collaborators assignment repos)"""
        query = """
        query($org: String!) {
          organization(login: $org) {
            repositories(first: 100) {
              nodes {
                collaborators(first: 100) {
                  nodes {
                    login
                    name
                  }
                }
              }
            }
          }
        }
        """

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.GRAPHQL_URL,
                headers=self.headers,
                json={"query": query, "variables": {"org": org_login}}
            )
            resp.raise_for_status()
            data = resp.json()

        students = set()

        repos = data["data"]["organization"]["repositories"]["nodes"]

        for repo in repos:
            collaborators = repo.get("collaborators", {}).get("nodes", [])
            for col in collaborators:
                students.add(col["login"])

        return list(students)

    async def get_all_members_of_org(self, org_login: str):
        """Получить учителей и TAs"""
        query = """
        query($org: String!, $cursor: String) {
          organization(login: $org) {
            membersWithRole(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                login
                name
              }
            }
          }
        }
        """

        members = []
        cursor = None

        async with httpx.AsyncClient() as client:
            while True:
                variables = {"org": org_login, "cursor": cursor}

                resp = await client.post(
                    self.GRAPHQL_URL,
                    headers=self.headers,
                    json={"query": query, "variables": variables}
                )
                resp.raise_for_status()
                data = resp.json()

                block = data["data"]["organization"]["membersWithRole"]

                members.extend(block["nodes"])

                if not block["pageInfo"]["hasNextPage"]:
                    break

                cursor = block["pageInfo"]["endCursor"]

        return members

    async def get_all(self):
        """Главный метод: курсы + учителя + студенты + задания"""

        orgs = await self.get_orgs()
        courses = []

        for org_login in orgs:
            teachers = await self.get_all_members_of_org(org_login)
            students = await self.get_students_from_org(org_login)
            assignments = await self.get_assignments_from_org(org_login)

            courses.append({
                "org": org_login,
                "teachers": teachers,
                "students": [{"login": s} for s in students],
                "assignments": assignments,
            })

        return courses

    async def test_connection(self) -> bool:
        try:
            await self.get_orgs()
            return True
        except Exception:
            return False

async def main():
    gh = GitHubClassroomClient()

    print("Testing GitHub connection...")
    print("OK?", await gh.test_connection())

    print("\nFetching classroom data...")
    courses = await gh.get_orgs()

    # for c in courses:
    #     print("===================================")
    #     print(f"Course (organization): {c['org']}")
    #     print("-----------------------------------")
    #
    #     print("Teachers / TAs:")
    #     for t in c["teachers"]:
    #         print("   -", t["login"])
    #
    #     print("Students:")
    #     for s in c["students"]:
    #         print("   -", s["login"])
    #
    #     print("Assignments:")
    #     for a in c["assignments"]:
    #         print("   -", a["name"], "→", a["url"])
    #
    #     print("===================================\n")


if __name__ == "__main__":
    asyncio.run(main())
