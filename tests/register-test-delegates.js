/**
 * Register test delegates for DISEC and PNA committees
 */

const API_URL = 'http://localhost:8000';

const delegates = [
  // DISEC (ID: 13) - 5 delegates
  {
    full_name: "Ahmed Hassan",
    student_id_cnic: "DISEC-2026-001",
    email: "ahmed.hassan@student.edu",
    phone: "+923001234567",
    institution: "Lahore University",
    committee_id: 13
  },
  {
    full_name: "Fatima Khan",
    student_id_cnic: "DISEC-2026-002",
    email: "fatima.khan@student.edu",
    phone: "+923001234568",
    institution: "Punjab University",
    committee_id: 13
  },
  {
    full_name: "Omar Sheikh",
    student_id_cnic: "DISEC-2026-003",
    email: "omar.sheikh@student.edu",
    phone: "+923001234569",
    institution: "UET Lahore",
    committee_id: 13
  },
  {
    full_name: "Aisha Malik",
    student_id_cnic: "DISEC-2026-004",
    email: "aisha.malik@student.edu",
    phone: "+923001234570",
    institution: "GC University",
    committee_id: 13
  },
  {
    full_name: "Bilal Ahmed",
    student_id_cnic: "DISEC-2026-005",
    email: "bilal.ahmed@student.edu",
    phone: "+923001234571",
    institution: "University of Karachi",
    committee_id: 13
  },
  // PNA (ID: 15) - 5 delegates
  {
    full_name: "Muhammad Ali",
    student_id_cnic: "PNA-2026-001",
    email: "muhammad.ali@student.edu",
    phone: "+923001234572",
    institution: "LUMS",
    committee_id: 15
  },
  {
    full_name: "Sara Williams",
    student_id_cnic: "PNA-2026-002",
    email: "sara.williams@student.edu",
    phone: "+923001234573",
    institution: "Beaconhouse School",
    committee_id: 15
  },
  {
    full_name: "Usman Dar",
    student_id_cnic: "PNA-2026-003",
    email: "usman.dar@student.edu",
    phone: "+923001234574",
    institution: "NUST",
    committee_id: 15
  },
  {
    full_name: "Zainab Abbas",
    student_id_cnic: "PNA-2026-004",
    email: "zainab.abbas@student.edu",
    phone: "+923001234575",
    institution: " Kinnaird College",
    committee_id: 15
  },
  {
    full_name: "Hamza Rashid",
    student_id_cnic: "PNA-2026-005",
    email: "hamza.rashid@student.edu",
    phone: "+923001234576",
    institution: "FAST-NU",
    committee_id: 15
  }
];

async function registerDelegate(d) {
  try {
    const response = await fetch(`${API_URL}/api/v1/delegates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d)
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Registered: ${d.full_name} (${d.committee_id === 13 ? 'DISEC' : 'PNA'}) - Roll: ${data.data?.delegate?.roll_number || 'N/A'}`);
      return data;
    } else {
      const err = await response.json();
      console.log(`⚠️ ${d.full_name}: ${err.detail || 'Failed'}`);
      return null;
    }
  } catch (e) {
    console.log(`❌ Error registering ${d.full_name}: ${e.message}`);
    return null;
  }
}

async function main() {
  console.log('Registering test delegates for DISEC and PNA...\n');

  let disecCount = 0;
  let pnaCount = 0;

  for (const d of delegates) {
    await registerDelegate(d);
    await new Promise(r => setTimeout(r, 300)); // Small delay between registrations
  }

  // Check final counts
  const comms = await fetch(`${API_URL}/api/v1/committees`).then(r => r.json());
  const disec = comms.data.committees.find(c => c.id === 13);
  const pna = comms.data.committees.find(c => c.id === 15);

  console.log(`\n📊 Final Counts:`);
  console.log(`   DISEC: ${disec.filled_seats} delegates`);
  console.log(`   PNA: ${pna.filled_seats} delegates`);
}

main();
