/*
 * LGU MUN 2026 - Load Test Script
 * Tests 450 concurrent users using k6
 *
 * To run: k6 run load-test.js
 * Or: k6 archive load-test.js -o load-test.tar && k6 run load-test.tar
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';

// Custom metrics
const registrationSuccess = new Counter('registration_success');
const registrationFailed = new Counter('registration_failed');
const transferSuccess = new Counter('transfer_success');
const transferFailed = new Counter('transfer_failed');
const responseTime = new Trend('response_time');
const errorRate = new Rate('error_rate');

// Configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:8000';
const COMMITTEE_IDS = [17, 18, 19, 20, 21, 22, 23, 24, 25]; // All 9 committees

export const options = {
  // Smoke test - 10 users
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
    },
    // Load test - 100 concurrent users
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
      ],
    },
    // Stress test - 450 concurrent users (max capacity)
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 200 },
        { duration: '1m', target: 400 },
        { duration: '1m', target: 450 }, // Max capacity
        { duration: '30s', target: 0 },
      ],
    },
    // Spike test - sudden burst
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 0 },
        { duration: '5s', target: 450 }, // Sudden spike
        { duration: '10s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.05'], // Less than 5% failure
    error_rate: ['rate<0.1'], // Less than 10% errors
  },
};

export default function () {
  const timestamp = __VU * 1000 + Date.now();
  const committeeId = COMMITTEE_IDS[__VU % 9];

  // Test 1: Register new delegate
  const registerData = {
    full_name: `LoadTest Delegate ${timestamp}`,
    email: `loadtest_${timestamp}@test.com`,
    phone: `0300${String(timestamp).slice(-7)}`,
    institution: 'Load Test University',
    student_id: `LOAD${timestamp}`,
    committee_id: committeeId,
  };

  const registerStart = Date.now();
  const registerRes = http.post(
    `${BASE_URL}/api/v1/delegates`,
    JSON.stringify(registerData),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  responseTime.add(Date.now() - registerStart);

  if (registerRes.status() === 201) {
    registrationSuccess.add(1);
  } else {
    registrationFailed.add(1);
    errorRate.add(1);
  }

  check(registerRes, {
    'Registration status is 201 or 400': (r) =>
      r.status === 201 || r.status === 400 || r.status === 409,
  });

  sleep(1);

  // Test 2: Get committees
  const committeesStart = Date.now();
  const committeesRes = http.get(`${BASE_URL}/api/v1/committees`);
  responseTime.add(Date.now() - committeesStart);

  check(committeesRes, {
    'Committees endpoint OK': (r) => r.status === 200,
  });

  sleep(0.5);

  // Test 3: Get delegate count
  const countRes = http.get(`${BASE_URL}/api/v1/delegates/count`);

  check(countRes, {
    'Count endpoint OK': (r) => r.status === 200,
  });

  sleep(0.5);
}

// Test special scenarios
export function handleSpecialEvents() {
  return {
    // Test committee seat limits
    test_seat_limits: () => {
      const res = http.get(`${BASE_URL}/api/v1/committees`);
      const committees = JSON.parse(res.body).data.committees;

      let allUnderLimit = true;
      for (const committee of committees) {
        if (committee.filled_seats > committee.total_seats) {
          allUnderLimit = false;
        }
      }

      return {
        seat_limits_respected: allUnderLimit,
      };
    },
  };
}