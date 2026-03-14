#!/usr/bin/env node
/**
 * Generates airportCoordinates.js from the mwgg/Airports database.
 * Run: node scripts/generate-airport-coordinates.cjs
 * Or: npm run generate:airports (if script added to package.json)
 */
const fs = require('fs')
const path = require('path')
const https = require('https')

const SOURCE_URL = 'https://raw.githubusercontent.com/mwgg/Airports/master/airports.json'
const OUTPUT_PATH = path.join(__dirname, '../src/data/airport_coordinates/airportCoordinates.js')

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => resolve(JSON.parse(data)))
    }).on('error', reject)
  })
}

async function main() {
  let data
  const localPath = path.join(__dirname, '../../airports.json')
  if (fs.existsSync(localPath)) {
    data = JSON.parse(fs.readFileSync(localPath, 'utf8'))
    console.log('Using local airports.json')
  } else {
    console.log('Fetching from GitHub...')
    data = await fetch(SOURCE_URL)
  }

  const out = {}
  for (const a of Object.values(data)) {
    if (!a.iata || a.iata.length !== 3) continue
    const key = a.iata.toUpperCase()
    if (out[key]) continue // keep first occurrence, skip duplicates
    out[key] = [a.lon, a.lat]
  }

  const entries = Object.entries(out).sort((a, b) => a[0].localeCompare(b[0]))
  const lines = ['export const AIRPORT_COORDINATES = {']
  for (let i = 0; i < entries.length; i++) {
    const [code, coord] = entries[i]
    const comma = i < entries.length - 1 ? ',' : ''
    lines.push(`  ${code}: [${coord[0]}, ${coord[1]}]${comma}`)
  }
  lines.push('}')

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true })
  fs.writeFileSync(OUTPUT_PATH, lines.join('\n'))
  console.log(`Wrote ${entries.length} airports to ${OUTPUT_PATH}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
