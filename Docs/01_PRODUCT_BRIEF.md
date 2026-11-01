# 01 — Product Brief

## Product
**CivicPilot — Government Scheme Discovery & Application Assistant**

## Problem
Citizens often struggle to find relevant public schemes, interpret official notifications, understand eligibility, assemble supporting documents, and navigate application steps. Information is fragmented across official portals and PDFs.

## Target user for the MVP
Indian college students looking for scholarships. Keep the underlying data model extensible to other citizen groups and scheme categories, but do not attempt nationwide coverage in the first release.

## Product promise
Help a student:
1. Describe their circumstances once.
2. Discover potentially relevant scholarships.
3. Understand why each scheme may or may not fit.
4. Ask questions grounded in official source material.
5. Identify documents they may need.
6. Prepare an application using a review-before-action workflow.

## Core user journey
Landing page → profile setup → scheme recommendations → scheme detail → ask a grounded question → upload optional documents → review extracted facts → eligibility assessment → prepare a demo application → user review.

## Trust and transparency
- CivicPilot is an independent information assistant, not a government department or official portal.
- Display the official source and last-verified date for every scheme.
- Separate confirmed facts, inferred matches, and unknown information.
- Use “potentially eligible” rather than guaranteeing eligibility.
- Show the rules and profile facts behind every eligibility result.
- Do not fabricate deadlines, benefit amounts, application status, or portal receipts.
- Provide a correction/report-source action for questionable information.

## MVP success criteria
A new user can complete the core journey without developer intervention. At least 10 verified scheme records are available. Answers cite source documents. Eligibility results are deterministic and explainable. Uploads are private. Demo application preparation works against a controlled local/demo form.

## Out of scope for the first week
- Every government scheme in India.
- Production submission to real government portals.
- Legal advice or guaranteed eligibility.
- Native mobile apps.
- Complex multi-agent swarms.
- Voice calling, payment processing, social feeds, or public user profiles.
