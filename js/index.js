#!/usr/bin/env node

const commander = require("commander");
const express = require("express");
const axios = require("axios");

commander
	.option("--port <value>", "Port.", 3000)
	.option("--registry <value>", "Registry.", "https://registry.npmjs.org")
	.option("--timeout <value>", "Timeout.", 120)
	.option("--max-date <value>", "Max date.", "2022-02-02")
	.parse();
const opts = commander.opts();

const proxy = async (req, res) => {
	const url = decodeURIComponent(req.url);
	console.log(url);

	let response;
	try {
		response = await axios({
			url: opts.registry + url,
			timeout: opts.timeout * 1000,
			validateStatus: status => status === 200,
			responseType: "arraybuffer"
		});
	} catch (e) {
		console.log(e);
		return res.status(500).send();
	}

	const contentType = response.headers["content-type"];

	if (contentType.startsWith("application/json")) {
		const data = JSON.parse(response.data);
		const {versions, time} = data;
		const newTime = {
			created: time.created,
			modified: time.modified
		};
		for (const version of Object.keys(time)) {
			const ts = time[version];
			const date = ts.substring(0, 10);
			if (date <= opts.maxDate) {
				newTime[version] = ts;
			} else {
				delete versions[version];
			}
		}
		data.time = newTime;

		return res.json(data);
	}

	return res.contentType(contentType).send(response.data);
};

const app = express();
app.get(/\/.*?/, proxy)
app.listen(opts.port, () => console.log(`Proxy listening on port ${opts.port}`));
