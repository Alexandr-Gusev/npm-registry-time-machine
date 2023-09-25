# NPM registry time machine

Proxy for limiting the release dates of packages.

## Usage

Run proxy:
```bash
npm-registry-time-machine --port 3000 --registry https://registry.npmjs.org --timeout 120 --max-date 2022-02-02
```

Set proxy as registry:
```bash
npm config set registry http://127.0.0.1:3000
```

Now all packages with a release date exceeding the maximum date are hidden for npm.

## How it works

This tool is a proxy between npm and the registry. The proxy receives requests from npm and sends them to the registry. Information about packages with a release date exceeding the maximum date is removed from the response. After that, the response is returned to npm. Therefore, npm uses only those packages that were released no later than the maximum date.
