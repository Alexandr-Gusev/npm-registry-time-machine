import argparse
from aiohttp import web
from aiohttp_requests import requests
from urllib.parse import urljoin, urlparse


def fix_tarball(url, registry):
    t = urlparse(url)
    return registry + url[len(t.scheme) + 3 + len(t.netloc):].replace("%2f", "/")


async def proxy(request):
    path = request.match_info["path"]
    print(path)

    response = await requests.get(urljoin(args.registry, path), timeout=args.timeout)

    content_type = response.headers["content-type"]

    if content_type.startswith("application/json"):
        data = await response.json()

        name = data["name"]
        versions = data["versions"]
        time = data["time"]
        new_time = {
            "created": time["created"],
            "modified": time["modified"]
        }
        for version, ts in time.items():
            date = ts[:10]
            if date <= args.max_date or name in args.trusted_packages:
                new_time[version] = ts
                if versions.get(version) and versions[version].get("dist") and versions[version]["dist"].get("tarball"):
                    versions[version]["dist"]["tarball"] = fix_tarball(versions[version]["dist"]["tarball"], args.registry)
            else:
                versions.pop(version, None)
        data["time"] = new_time

        return web.json_response(data)

    return web.Response(content_type=content_type, body=await response.read())


def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=3000, type=int)
    parser.add_argument("--registry", default="https://registry.npmjs.org", type=str)
    parser.add_argument("--timeout", default=120, type=int)
    parser.add_argument("--max-date", default="2022-02-02", type=str)
    parser.add_argument("--trusted-packages", nargs="*", type=str)
    args = parser.parse_args()

    app = web.Application()
    app.add_routes([
        web.get("/{path:.*?}", proxy)
    ])
    web.run_app(app, port=args.port)


if __name__ == "__main__":
    main()
