# PROJECT TECHNICAL DESIGN

## Service Booking Application

---

# Task 1 — Business Requirement Analysis

## Business Requirement

A mobile user should be able to register, create a profile, search available services, view service details, make a booking, receive notifications, communicate with the service provider, and track the booking status.

## Users

1. Customer
2. Service Provider
3. Admin

## Roles

### Customer
- Register and login
- Manage personal profile
- Search available services
- View service details
- Create bookings
- Make payments
- Track booking status
- Receive notifications
- Communicate with service providers

### Service Provider
- Login
- Manage provider profile
- Create and manage services
- View bookings
- Accept or reject bookings
- Update booking status
- Communicate with customers
- Receive notifications

### Admin
- Manage users
- Manage service providers
- Manage services
- Manage bookings
- Monitor payments
- Manage notifications
- Review system activity

## Modules

1. Authentication
2. User Profile
3. Service Provider
4. Services
5. Search
6. Booking
7. Payment
8. Notifications
9. Chat
10. Admin

## Required APIs

- Authentication APIs
- Profile APIs
- Provider APIs
- Service APIs
- Search APIs
- Booking APIs
- Payment APIs
- Notification APIs
- Chat APIs
- Admin APIs

## Database Entities

- User
- Profile
- ServiceProvider
- Service
- Booking
- Payment
- Notification
- ChatConversation
- ChatMessage

---

# Task 2 — User Role Permissions

## Admin

### Can See
- All users
- All providers
- All services
- All bookings
- Payment information
- System notifications
- Audit information

### Can Create
- Administrative records
- System configuration records

### Can Update
- Users
- Providers
- Services
- Bookings
- System configuration

### Can Delete
- Authorized users
- Services
- Other authorized records according to system policy

---

## Customer

### Can See
- Own profile
- Available services
- Service details
- Own bookings
- Own payments
- Own notifications
- Own chat conversations

### Can Create
- Profile
- Bookings
- Payments
- Chat messages

### Can Update
- Own profile
- Booking where permitted
- Chat messages where permitted

### Can Delete
- Own profile information where permitted
- Own data according to retention policy

---

## Service Provider

### Can See
- Own profile
- Own services
- Assigned bookings
- Payment information related to own services
- Own notifications
- Customer conversations related to bookings

### Can Create
- Services
- Chat messages
- Provider profile

### Can Update
- Own profile
- Own services
- Booking status
- Chat messages where permitted

### Can Delete
- Own services
- Own records where permitted

---

# Task 3 — Modules

## 1. Authentication
- Registration
- Login
- Logout
- JWT authentication
- Token refresh
- Password change
- Password reset

## 2. User Profile
- Create profile
- View profile
- Update profile
- Profile image
- Contact information

## 3. Service Provider
- Provider registration
- Provider profile
- Provider verification
- Provider availability
- Provider service management

## 4. Services
- Create service
- List services
- Service details
- Update service
- Deactivate service
- Delete service

## 5. Search
- Search services
- Category filtering
- Price filtering
- Provider filtering
- Availability filtering
- Pagination

## 6. Booking
- Create booking
- View booking
- Accept booking
- Reject booking
- Cancel booking
- Complete booking
- Track booking status

## 7. Payment
- Create payment
- Payment verification
- Payment status
- Transaction reference
- Payment webhook

## 8. Notifications
- Booking notifications
- Payment notifications
- Status notifications
- Read/unread notifications

## 9. Chat
- Customer-provider conversation
- Send messages
- Receive messages
- Message read status
- Real-time communication

## 10. Admin
- User management
- Provider management
- Service management
- Booking management
- Payment monitoring
- Audit monitoring

---

# Task 4 — Database Design

## User

- id
- email
- password
- role
- is_active
- created_at
- updated_at

## Profile

- id
- user_id
- full_name
- phone
- address
- profile_image
- created_at
- updated_at

## ServiceProvider

- id
- user_id
- business_name
- description
- verification_status
- is_available
- created_at
- updated_at

## Service

- id
- provider_id
- name
- description
- category
- price
- duration
- is_active
- created_at
- updated_at

## Booking

- id
- customer_id
- service_id
- provider_id
- scheduled_at
- status
- total_amount
- created_at
- updated_at

## Payment

- id
- booking_id
- amount
- transaction_reference
- status
- paid_at
- created_at

## Notification

- id
- user_id
- booking_id
- notification_type
- title
- message
- is_read
- created_at

## ChatConversation

- id
- booking_id
- customer_id
- provider_id
- created_at

## ChatMessage

- id
- conversation_id
- sender_id
- message
- is_read
- created_at

## ER Diagram

```text
                         USER
                          |
             +------------+------------+
             |                         |
          PROFILE              SERVICE PROVIDER
                                      |
                                      |
                                   SERVICE
                                      |
                                      |
                                  BOOKING
                                /    |     \
                               /     |      \
                         CUSTOMER  SERVICE  PROVIDER
                               |
                            PAYMENT

BOOKING
   |
   +---- NOTIFICATION

BOOKING
   |
   +---- CHAT CONVERSATION
              |
              +---- CHAT MESSAGE
