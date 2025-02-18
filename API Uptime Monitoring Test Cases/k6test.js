import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 100 },   // Ramp up
    { duration: '10m', target: 100 },  // Stay at peak
    { duration: '5m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'], // 95% of requests must complete under 300ms
    http_req_failed: ['rate<0.01'],  // Less than 1% of requests can fail
  },
};

export default function() {
  const BASE_URL = __ENV.API_BASE_URL;  // api.prod.gomoney.global
  const API_TOKEN = __ENV.API_TOKEN;

  const params = {
    headers: {
      'Authorization': `Bearer ${API_TOKEN}`,
    },
  };

  const responses = http.batch([
    ['GET', `${BASE_URL}/health`, null, params],
    ['GET', `${BASE_URL}/api/v1/status`, null, params],
    ['GET', `${BASE_URL}/api/v1/metrics`, null, params],
  ]);

  responses.forEach(response => {
    check(response, {
      'is status 200': (r) => r.status === 200,
      'response time < 300ms': (r) => r.timings.duration < 300,
    });
  });

  sleep(1);
}
