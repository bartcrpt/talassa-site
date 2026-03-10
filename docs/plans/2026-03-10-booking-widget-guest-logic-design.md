# Booking Widget Guest Logic Design

Date: 2026-03-10

## Goal

Bring the public booking widget on `/book` in line with the main booking flow on `/book/<id>`.

## Scope

- Replace the simple children field in the public booking widget with a guest picker:
  - adults (14+)
  - children 6-13
  - children up to 5
- Replace plain date inputs in the public widget with the same modal calendar pattern used on the booking page.
- When selecting check-out after check-in, the calendar should open on the same month as the selected check-in/check-out context.
- Update backend search and pricing to accept `children_under_five` alongside `adults` and `children`.

## Behavioral Rules

- Adults: 14+
- Children: 6-13
- Children up to 5 are tracked separately.
- Public search should mirror the current `/book/<id>` behavior for pricing and occupancy logic.
- Extra charge rules remain:
  - 01.05-31.10: children up to 5 -> 0, children 6-13 -> 1500, adults 14+ -> 2500
  - 01.11-30.04: children up to 5 -> 0, children 6-13 -> 1000, adults 14+ -> 2000

## Implementation

- `templates/public/book.html`
  - add date range modal UI
  - add guest dropdown UI and hidden fields
  - add JS for date range behavior and guest counters
- `static/css/site.css`
  - add styles for the public guest picker and calendar modal block
- `app.py`
  - accept and forward `children_under_five` in `/book`, `/book/<id>`, combination flow, and `calcPrice`
  - update result captions and URLs
- `services/rooms.py`
  - extend total-price calculation signature to accept `children_under_five`
  - keep pricing behavior aligned with the booking page

## Notes

- This intentionally reuses the existing booking page behavior instead of inventing a second guest model.
- Combination booking continues to distribute adults and children 6-13 across two rooms; children up to 5 remain a separate shared field for the booking flow.
