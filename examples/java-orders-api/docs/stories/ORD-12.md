# ORD-12: Add an endpoint to cancel an order

> SYNTHETIC user story for demo purposes. Not from a real backlog.

## Story

As a customer support agent,
I want to cancel an order that has not shipped yet,
so that the customer is not charged for something they no longer want.

## Acceptance criteria

- **Given** an order exists with status `CREATED`
  **When** I send a cancel request for that order id
  **Then** the order status becomes `CANCELLED`
  **And** the response returns the updated order

## Notes

- Endpoint shape is up to the team.
