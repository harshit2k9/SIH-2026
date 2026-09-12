 const crypto = require('crypto');

function computeHash(prevHash, entry) {
  const dataString = JSON.stringify(entry) + prevHash;
  return crypto.createHash('sha256').update(dataString).digest('hex');
}

function verifyChain(entries) {
  let expectedPrevHash = '0'.repeat(64);
  for (let i = 0; i < entries.length; i++) {
    const recalculatedHash = computeHash(expectedPrevHash, entries[i].data);
    if (recalculatedHash !== entries[i].hash) {
      return { valid: false, tamperedAt: i };
    }
    expectedPrevHash = entries[i].hash;
  }
  return { valid: true };
}

const genesisHash = '0'.repeat(64);
let chain = [];
let prevHash = genesisHash;

const actions = [
  { action: "CREATED", user: "Officer A", time: "2026-08-30T10:00:00Z" },
  { action: "VIEWED", user: "Officer B", time: "2026-08-30T10:05:00Z" },
  { action: "UPLOADED", user: "Officer C", time: "2026-08-30T10:10:00Z" },
  { action: "SIGNED", user: "Officer D", time: "2026-08-30T10:15:00Z" }
];

actions.forEach((entryData) => {
  const hash = computeHash(prevHash, entryData);
  chain.push({ data: entryData, hash: hash });
  console.log(`${entryData.action} by ${entryData.user} -> hash: ${hash}`);
  prevHash = hash;
});

console.log("\n--- Verification (no tampering) ---");
console.log(verifyChain(chain));

console.log("\n--- Tampering Test ---");
chain[1].data.user = "Officer B (HACKED)";
console.log(verifyChain(chain));