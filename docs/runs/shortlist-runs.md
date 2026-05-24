# Shortlist Runs

Each run from `scripts/run_shortlist.py` is appended below so rounds can be compared.
Commute times are Google Routes API peak estimates (pessimistic traffic), morning ~9am
and evening ~6pm local. Society names come from Google Places (names only; size and
parking are not verifiable from this source - see notes per run).

---

## SAMPLE (stub data, NOT real) - format demo (24-05-2026 15:30)

- City: Mumbai | Mode: own_car | Budget: 80000 | Commute target: <= 30 min both peaks
- Office: 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
- Preferences: four-wheeler parking, apartments at least 500 sq ft, commute under 30 min both peaks, monsoon/flooding aware

| Area | Morning | Evening | Meets target | Confidence | Societies |
|---|---|---|---|---|---|
| North Quarter | ~39m | ~45m | no | 0.52 | North Quarter Heights, North Quarter Residency, North Quarter Greens |
| Old Town | ~39m | ~45m | no | 0.52 | Old Town Heights, Old Town Residency, Old Town Greens |
| Green Meadows | ~39m | ~45m | no | 0.52 | Green Meadows Heights, Green Meadows Residency, Green Meadows Greens |
| Riverside | ~46m | ~52m | no | 0.48 | Riverside Heights, Riverside Residency, Riverside Greens |
| Tech Park East | ~46m | ~52m | no | 0.48 | Tech Park East Heights, Tech Park East Residency, Tech Park East Greens |

Sentiment / notes:
- **North Quarter**: Residents call it well-connected and green, with the usual peak-hour traffic.
- **Old Town**: Residents call it well-connected and green, with the usual peak-hour traffic.
- **Green Meadows**: Residents call it well-connected and green, with the usual peak-hour traffic.
- **Riverside**: Residents call it well-connected and green, with the usual peak-hour traffic.
- **Tech Park East**: Residents call it well-connected and green, with the usual peak-hour traffic.

---
## Shreya - Goregaon East round 1 (full real) (24-05-2026 15:39)

### Prompt

```
I am looking to shift to an office in Goregaon East, but I am a person from Delhi and I don't understand Mumbai at all. I would want to understand the localities that one can consider near Goregaon East for their relocation. Besides just knowing the localities, I would also want the name of the apartments with at least 500 sq ft of location space and a four-wheeler parking. While giving the results, please optimize on the time to travel to the office, both morning and evening, expecting it to be between 30 minutes. Please do consider the raining season, etc., and the traffic that happens in Mumbai. These are the only pre-limitations that I have as of now.

Office addrss - 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
```

### Parsed brief

- City: Mumbai | Mode: own_car | Budget: 80000 (not specified; non-binding) | Commute target: <= 30 min both peaks
- Office: 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
- Preferences: four-wheeler parking, apartments at least 500 sq ft, commute under 30 min both peaks, monsoon/flooding aware
- NOTE: this round predates the same-area commute fix (see Goregaon East ~977m below) and the monsoon flag.

| Area | Morning | Evening | Meets target | Confidence | Societies |
|---|---|---|---|---|---|
| Jogeshwari East | ~12m | ~10m | yes | 0.78 | Kaatyayni Heights, Veda - Sangam Lifespaces, Sunteck City 4th Avenue, Goregaon, Kalpataru Estate Bldg No 5, Kalpataru Estate Bldg No 2 |
| Malad East | ~13m | ~25m | yes | 0.71 | Omkar Alta Monte, Malad, Exquisite by Oberoi Realty, Omkar Signet, Malad, Kalpataru Gardens 1, OCTACREST |
| Goregaon West | ~17m | ~23m | yes | 0.63 | Kalpataru Radiance, Lodha Fiorenza, Sunteck City Avenue 1, Windermere, MHADA 412 PAHADI GOREGAON PMAY |
| Andheri East | ~35m | ~22m | no | 0.57 | Kaatyayni Heights, Veda - Sangam Lifespaces, Pearl Heaven, Anmol Society, Palmrose Hubtown |
| Kandivali East | ~23m | ~42m | no | 0.53 | Whispering Palms Xxclusive, Alpine by SD Corp, Kandivali East, Sarova Experience Lounge, OCTACREST, Oberoi Park View |
| Goregaon East | ~977m | ~1120m | no | 0.35 | Kalpataru Radiance, Lodha Fiorenza, Exquisite by Oberoi Realty, Sunteck City Avenue 1, Vasant Valley Complex |

Sentiment / notes:
- **Jogeshwari East**: Jogeshwari East offers excellent connectivity via highway and metro, but experiences significant traffic congestion. While generally considered safe with good amenities, residents note concerns about overcrowding, pollut
- **Malad East**: Malad East offers excellent connectivity and a good range of amenities like markets and hospitals, with residents generally feeling safe due to frequent patrolling. However, significant traffic congestion and parking dif
- **Goregaon West**: Goregaon West offers good connectivity and amenities like schools, hospitals, and markets, though commute and traffic can be challenging. While generally considered safe, with a good quality of life appealing to families
- **Andheri East**: Andheri East offers excellent connectivity and a wealth of amenities, contributing to a convenient and vibrant quality of life with good social infrastructure. However, residents frequently experience heavy traffic conge
- **Kandivali East**: Kandivali East offers convenient amenities and a safe environment with a strong community feel, but residents experience significant challenges with traffic congestion, parking, and waterlogging, which impact commute tim
- **Goregaon East**: Goregaon East offers good amenities and a generally peaceful quality of life with green spaces, but experiences significant traffic congestion and mixed safety perceptions in different areas. While public transport is ac

---
## Shreya - Goregaon East round 2 (1BHK, 50k, semi-furnished) (24-05-2026 15:51)

### Prompt

```
I am looking to shift to an office in Goregaon East, but I am a person from Delhi and I don't understand Mumbai at all. I would want to understand the localities that one can consider near Goregaon East for their relocation. Besides just knowing the localities, I would also want the name of the apartments with at least 500 sq ft of location space and a four-wheeler parking. While giving the results, please optimize on the time to travel to the office, both morning and evening, expecting it to be between 30 minutes. Please do consider the raining season, etc., and the traffic that happens in Mumbai. These are the only pre-limitations that I have as of now.

BHK - 1 BHK
Budget - 50,000 INR
Semi furnished flat
Office addrss - 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
```

### Parsed brief

- City: Mumbai | Mode: own_car | Budget: 50000 | Commute target: <= 30 min both peaks
- Office: 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
- Preferences: 1 BHK, semi-furnished, four-wheeler parking, at least 500 sq ft, commute under 30 min both peaks, monsoon/flooding aware

### Output

| Area | Morning | Evening | Meets target | Monsoon | Confidence | Societies |
|---|---|---|---|---|---|---|
| Jogeshwari East | ~12m | ~10m | yes | - | 0.78 | Kaatyayni Heights, Veda - Sangam Lifespaces, Sunteck City 4th Avenue, Goregaon, Kalpataru Estate Bldg No 5, Kalpataru Estate Bldg No 2 |
| Goregaon West | ~17m | ~23m | yes | - | 0.72 | Kalpataru Radiance, Lodha Fiorenza, Sunteck City Avenue 1, Windermere, MHADA 412 PAHADI GOREGAON PMAY |
| Malad East | ~13m | ~25m | yes | flag | 0.61 | Omkar Alta Monte, Malad, Exquisite by Oberoi Realty, Omkar Signet, Malad, Kalpataru Gardens 1, OCTACREST |
| Kandivali East | ~23m | ~42m | no | flag | 0.52 | Whispering Palms Xxclusive, Alpine by SD Corp, Kandivali East, Sarova Experience Lounge, OCTACREST, Oberoi Park View |
| Goregaon East | unreliable | unreliable | n/a | - | 0.35 | Kalpataru Radiance, Lodha Fiorenza, Exquisite by Oberoi Realty, Sunteck City Avenue 1, Vasant Valley Complex |

Sentiment / notes:
- **Jogeshwari East**: Jogeshwari East offers good connectivity with public transport, though traffic and noise pollution are noted concerns. The area is generally perceived as safe with abundant amenities like markets, schools, and hospitals,
- **Goregaon West**: Goregaon West offers good amenities and a safe environment, with convenient access to public transport despite traffic challenges. While quality of life is generally high due to social infrastructure and dining options, 
- **Malad East**: Malad East is praised for its strong amenities, including schools, hospitals, and markets, and is considered safe, especially in gated communities. While traffic congestion on main roads is a notable drawback, good rail   _[Monsoon: Malad East falls in or near a known Mumbai waterlogging belt. Avoid ground/low floors, check the society's drainage and approach-road flooding before signing.]_
- **Kandivali East**: Kandivali East offers good connectivity and amenities like markets and schools, though commute and traffic are significant concerns. While generally safe with a positive community feel, some residents note issues with st  _[Monsoon: Kandivali East falls in or near a known Mumbai waterlogging belt. Avoid ground/low floors, check the society's drainage and approach-road flooding before signing.]_
- **Goregaon East**: Goregaon East offers good amenities and a decent quality of life with green spaces, but faces significant traffic congestion and mixed safety perceptions, particularly for women in less-lit areas. While well-connected by

Apartment filters (size >= 500 sq ft, four-wheeler parking, BHK, furnishing) are NOT verifiable from current data sources - check at listing/visit stage.

---
## Shreya - Goregaon East round 3 (listings + map links) (24-05-2026 16:06)

### Prompt

```
I am looking to shift to an office in Goregaon East, but I am a person from Delhi and I don't understand Mumbai at all. I would want to understand the localities that one can consider near Goregaon East for their relocation. Besides just knowing the localities, I would also want the name of the apartments with at least 500 sq ft of location space and a four-wheeler parking. While giving the results, please optimize on the time to travel to the office, both morning and evening, expecting it to be between 30 minutes. Please do consider the raining season, etc., and the traffic that happens in Mumbai. These are the only pre-limitations that I have as of now.

BHK - 1 BHK
Budget - 50,000 INR
Semi furnished flat
Office addrss - 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
```

### Parsed brief

- City: Mumbai | Mode: own_car | Budget: 50000 | Commute target: <= 30 min both peaks
- Office: 12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060
- Preferences: 1 BHK, semi-furnished, four-wheeler parking, at least 500 sq ft, commute under 30 min both peaks, monsoon/flooding aware

### Output

| Area | Morning | Evening | Meets target | Monsoon | Confidence | Verify on Maps | Societies |
|---|---|---|---|---|---|---|---|
| Goregaon West | ~17m | ~23m | yes | - | 0.72 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Goregaon+West%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Kalpataru Radiance, Lodha Fiorenza, Sunteck City Avenue 1, Windermere, MHADA 412 PAHADI GOREGAON PMAY |
| Malad East | ~13m | ~25m | yes | flag | 0.61 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Malad+East%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Omkar Alta Monte, Malad, Exquisite by Oberoi Realty, Omkar Signet, Malad, Kalpataru Gardens 1, OCTACREST |
| Borivali East | ~22m | ~41m | no | - | 0.53 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Borivali+East%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Rustomjee Summit, Country Park Phase 3, Rivali Park, Wintergreen A-Wing, Signia High by Sunteck Realty, Borivali, Royal Complex |
| Kandivali East | ~23m | ~42m | no | flag | 0.52 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Kandivali+East%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Whispering Palms Xxclusive, Alpine by SD Corp, Kandivali East, Sarova Experience Lounge, OCTACREST, Oberoi Park View |
| Andheri East | ~35m | ~22m | no | flag | 0.47 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Andheri+East%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Kaatyayni Heights, Veda - Sangam Lifespaces, Pearl Heaven, Anmol Society, Palmrose Hubtown |
| Goregaon East | unreliable | unreliable | n/a | - | 0.35 | [Open in Maps](https://www.google.com/maps/dir/?api=1&origin=Goregaon+East%2C+Mumbai&destination=12th+Floor%2C+Lotus+Corporate+Park%2C+F+Wing%2C+off+Western+Express+Highway%2C+Geetanjali+Railway+Colony%2C+Laxmi+Nagar%2C+Goregaon+East%2C+Mumbai%2C+Maharashtra+400060) | Kalpataru Radiance, Lodha Fiorenza, Exquisite by Oberoi Realty, Sunteck City Avenue 1, Vasant Valley Complex |

### Candidate listings (UNVERIFIED - grounded best-effort; confirm on the listing and at visit)

**Malad East**
- 1 BHK Flat in Prayag Heights, Dindoshi, Malad East: BHK ?, 650 sqft, INR 42000, semi-furnished, parking ? - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7MHUVBhDki_rTC2JWzidCI5rHtWASSzEkrQqfNZjJmjf0pDjBYXi3TMWfuUTqywUYb1YEhqwYE8gLhEKEqA5DPRkfe17ebCY1NE_BRK8hNO9Zpzkk-2gcORmDoQxB33KlspsIhhnnEiiP63o3oWa1SzEksSVNN5-eZKoOFd2pl4wDHx4cJ6AUekIVPBLqKYwvLjyjcw==)

**Borivali East**
- 1 BHK Apartment For Rent in Raghav Paradise, Borivali East: BHK ?, 690 sqft, INR 34000, Semi-Furnished, parking yes - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZ0BFusc6WdqykOSp89Wal5-0YGDb7VQHifks51x3F4VVHWUDxWaeDE1k4zd2F_qAqLXY0NYzVAmQqm8FpzNus0Hw0s3yUFNiw-Rx7jC3OKhHiWEdbGXpv26ggw4ScDniQbj9U6ykGiis5XhdwsApSmCKDT0YNFAV5Zax03ijXalE=)
- 1 BHK Flat for rent in Borivali East, Mumbai. HAWARE INTELLIGENTIA AX...: BHK ?, 1080 sqft, INR 46000, Semi-Furnished, parking yes - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYYQ6YWaxUrFnVND04iuvG5jEXKhZxREWaJaS6__DhhoKVY2ysFL9gB7NS6ER4q-E3w3_KGJgumpfsR0ZyIfkqwX6PmeZF7sUQK8eUgdKRuF81hORFo7k0Tiz9tHi2xcRIG2GNqlPD-1VRHumW_xCmsCs6N6zaH-uTbXcwvwTsfCZ2dsIao5LpQBnS5dOznxRquBwekR07EdGO2-PWRn7L0v3nMvBmZjqvBPFSmiA=)

**Kandivali East**
- 1 BHK Semi-Furnished Flat in Kandivali East with Covered Parking: BHK ?, 678 sqft, INR 27000, Semi-Furnished, parking yes - [link](https://www.squareyards.com/1-bhk-flats-for-rent-in-kandivali-east-mumbai)
- 1 BHK Semi-Furnished Flat in Lokhandwala Kandivali East: BHK ?, 525 sqft, INR 30000, Semi-Furnished, parking ? - [link](https://www.99acres.com/1-bhk-flats-for-rent-in-kandivali-east-mumbai-south)
- 1 BHK Semi-Furnished Flat in Bhoomi Hills, Thakur Village: BHK ?, 600 sqft, INR 35000, Semi-Furnished, parking ? - [link](https://www.99acres.com/1-bhk-apartments-flats-for-rent-in-kandivali-east-mumbai-below-50000-without-brokerage-id)
- 1 BHK Semi-Furnished Flat in Siddhi Apartment, Ashok Nagar: BHK ?, 530 sqft, INR 36000, Semi-Furnished, parking ? - [link](https://www.99acres.com/1-bhk-apartments-flats-for-rent-in-kandivali-east-mumbai-below-50000-without-brokerage-id)

**Andheri East**
- 1 BHK Flat for rent in Marol, Mumbai: BHK ?, 650 sqft, INR 50000, Semi-Furnished, parking yes - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGURVH6ijOqb-FblbGKuYwIcDj32zVZ_I6M_ys1OXJJTqnrl5NP48OdahwChN9gPKzpBRVbAZ5oiPQuLJWHdiaLoYEV23k8OswNicRGFpRN9ukrJNm0IT3cd8Fy6NEuaFibZOuIIHku_NqPbut07zjCgN4_ec4u-Mdx7EoRfFsY4yTg5-RLG8W4rhWZduZIzSyjM1IfVX7976DLAcuP2Gfc6bDDO2o5B48KYjiIDw==)
- 1 BHK Apartments / Flat for rent in Raje Shivaji Nagar, Marol: BHK ?, 550 sqft, INR 49000, semi-Furnished, parking ? - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-fTv9viKkIPlREUL5We8RanvcJ1MyqePtb4j-E76skHBhDn2qHvmq8q9SXW9lPac4lDxf00ec7pd8Yz4MBQ5bDjhaTMidDtyC9FAL6JyELRwDcJBGUsBpmWhoCCsb77rK_XJvhz2sTlGL4zp9PVWRWAN_udpsREWk63q6HkZ7dgei5cQCCio_fMC8LzELhMdQ-Vyxt6MiXikQkU8fuOqCHDVeM8sOt1yNzeoslAS3_PTq0qmxOFZw0xIvbTiwfvBWm5ZvIA==)

**Goregaon East**
- 1 BHK Flat for Rent in Hanuman Tekdi Goregaon East (IM Applaud 38): BHK ?, 500 sqft, INR 44999, Semi-Furnished, parking yes - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXptS_TTkA5EG-a7z9r-1wcE2fPEz5msfnhvS7yUhN_AJB9nT7-JVPoSvuZXn4-_AFFS-VFAzm7kaFBAJyDh7C_gGaXFMMIyxM7sX0egrCfziwFQLxvTwi19szkXnDqVg3eeqCfaAaauDGJUA3Qq14pmw-LNieTF1Tv7ZBN5QWkxyxjmLC-raItslYwiGQrZMwFJI=)
- 1 BHK Apartment For Rent in Sushanku Avenue 37, Goregaon East: BHK ?, 619 sqft, INR 42000, Semi-Furnished, parking yes - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-71dfCtq-YQqLSXcvX1w3HlWTsFPw8xQ_hsYwBACCQr7XjxmaWFY3JKQi8kumcWmsy58PzCBgC-AVc4zOqRuvS85DA4qRVp09-s_F4tf8rsJ06s0mFUxK4AqWVym1ub8_t9dSJpntWxilgwxSr6WbOBppvZLsm1ROY5-6kxyxjmLC-raItslYwiGQrZMwFJI=)
- 1 BHK Flat for Rent in Goregaon East, Mumbai (Built-up Area: 630 sq.ft): BHK ?, 630 sqft, INR 45000, Semi-Furnished, parking ? - [link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-71dfCtq-YQqLSXcvX1w3HlWTsFPw8xQ_hsYwBACCQr7XjxmaWFY3JKQi8kumcWmsy58PzCBgC-AVc4zOqRuvS85DA4qRVp09-s_F4tf8rsJ06s0mFUxK4AqWVym1ub8_t9dSJpntWxilgwxSr6WbOBppvZLsm1ROY5-6kxyxjmLC-raItslYwiGQrZMwFJI=)

Sentiment / notes:
- **Goregaon West**: Goregaon West offers good connectivity and amenities, including schools, hospitals, and markets, and is generally considered safe. However, traffic congestion during peak hours and limited parking are notable drawbacks, 
- **Malad East**: Malad East offers good connectivity and plentiful amenities, making for a convenient lifestyle, though it experiences significant traffic congestion and some residents note issues with overcrowding and noise. The area is  _[Monsoon: Malad East falls in or near a known Mumbai waterlogging belt. Avoid ground/low floors, check the society's drainage and approach-road flooding before signing.]_
- **Borivali East**: Borivali East offers excellent connectivity and a wealth of amenities, contributing to a good quality of life, particularly for families, due to its proximity to Sanjay Gandhi National Park. While generally safe and fami
- **Kandivali East**: Kandivali East offers good connectivity via major transport links and a safe, community-focused environment with ample amenities like schools, hospitals, and shopping centers. However, residents should be prepared for si  _[Monsoon: Kandivali East falls in or near a known Mumbai waterlogging belt. Avoid ground/low floors, check the society's drainage and approach-road flooding before signing.]_
- **Andheri East**: Andheri East is a well-connected and amenity-rich area, favored by professionals for its proximity to jobs and the airport, though it suffers from significant traffic congestion and parking challenges. While generally co  _[Monsoon: Andheri East falls in or near a known Mumbai waterlogging belt. Avoid ground/low floors, check the society's drainage and approach-road flooding before signing.]_
- **Goregaon East**: Goregaon East offers good amenities and a blend of urban and green spaces, though traffic congestion and high living costs are notable downsides. While generally safe with visible policing, some areas have concerns regar

Listing attributes (size, parking, BHK, furnishing, rent) are best-effort and UNVERIFIED - confirm on the listing page and at visit.

---
