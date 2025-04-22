const { MongoClient, ObjectId } = require('mongodb');
const uri = "mongodb+srv://tm3995:<db_password>@healthtracker.vc6hwcx.mongodb.net/?retryWrites=true&w=majority&appName=HealthTracker";
async function insertSampleData() {
  try {
    const client = await MongoClient.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });
    console.log("Connected to MongoDB Atlas");

    const db = client.db("health_metrics_tracker");

    // Sample user
    const userId = new ObjectId();
    const goalId = new ObjectId();
    
    // Insert sample user
    await db.collection("users").insertOne({
      "_id": userId,
      "username": "testuser",
      "email": "test@example.com",
      "password_hash": "$2b$10$X/xqHGcJHAA4PnUXg7TkLOfEh3QphdXRZp1vHJvnZUBQg3xLMg1yW", // hash for "password123"
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "height": {
        "value": 180,
        "unit": "cm"
      },
      "weight": {
        "value": 75,
        "unit": "kg"
      },
      "goals": [
        {
          "goal_id": goalId,
          "type": "weight_loss",
          "target_value": 70,
          "unit": "kg",
          "start_date": "2025-01-01",
          "target_date": "2025-06-01",
          "status": "in_progress"
        }
      ],
      "preferences": {
        "measurement_units": "metric",
        "notification_settings": {
          "email": true,
          "push": true,
          "sms": false
        },
        "privacy": {
          "share_data": false,
          "public_profile": false
        }
      },
      "created_at": new Date("2025-01-01T00:00:00Z"),
      "updated_at": new Date("2025-04-15T12:30:45Z"),
      "last_login": new Date("2025-04-20T08:15:30Z")
    });

    // Insert sample health metrics
    await db.collection("health_metrics").insertOne({
      "_id": new ObjectId(),
      "user_id": userId,
      "metric_type": "weight",
      "value": 74.5,
      "unit": "kg",
      "recorded_at": new Date("2025-04-20T08:00:00Z"),
      "source": "manual_entry",
      "device_id": "fitbit_scale_123",
      "notes": "Morning weight after breakfast",
      "tags": ["morning", "post-meal"],
      "location": {
        "type": "Point",
        "coordinates": [-73.9857, 40.7484]
      },
      "created_at": new Date("2025-04-20T08:05:00Z"),
      "updated_at": new Date("2025-04-20T08:05:00Z")
    });

    // Insert sample activity
    await db.collection("activities").insertOne({
      "_id": new ObjectId(),
      "user_id": userId,
      "activity_type": "running",
      "duration": {
        "value": 45,
        "unit": "minutes"
      },
      "distance": {
        "value": 5.2,
        "unit": "km"
      },
      "calories_burned": 420,
      "heart_rate": {
        "average": 145,
        "max": 175,
        "min": 110
      },
      "start_time": new Date("2025-04-20T06:30:00Z"),
      "end_time": new Date("2025-04-20T07:15:00Z"),
      "location": {
        "start": {
          "type": "Point",
          "coordinates": [-73.9857, 40.7484]
        },
        "end": {
          "type": "Point",
          "coordinates": [-73.9650, 40.7630]
        },
        "path": [
          [-73.9857, 40.7484],
          [-73.9800, 40.7550],
          [-73.9750, 40.7600],
          [-73.9650, 40.7630]
        ]
      },
      "elevation_gain": {
        "value": 35,
        "unit": "meters"
      },
      "weather": {
        "temperature": {
          "value": 18,
          "unit": "celsius"
        },
        "conditions": "partly_cloudy",
        "humidity": 65
      },
      "notes": "Morning run in Central Park",
      "tags": ["morning", "outdoor", "cardio"],
      "device_id": "garmin_forerunner_245",
      "created_at": new Date("2025-04-20T07:20:00Z"),
      "updated_at": new Date("2025-04-20T07:20:00Z")
    });

    // Insert sample nutrition log
    await db.collection("nutrition_logs").insertOne({
      "_id": new ObjectId(),
      "user_id": userId,
      "meal_type": "breakfast",
      "foods": [
        {
          "name": "oatmeal",
          "quantity": {
            "value": 1,
            "unit": "cup"
          },
          "calories": 150,
          "macronutrients": {
            "protein": {
              "value": 5,
              "unit": "g"
            },
            "carbohydrates": {
              "value": 27,
              "unit": "g"
            },
            "fat": {
              "value": 2.5,
              "unit": "g"
            },
            "fiber": {
              "value": 4,
              "unit": "g"
            }
          },
          "micronutrients": [
            {
              "name": "iron",
              "value": 1.8,
              "unit": "mg"
            },
            {
              "name": "calcium",
              "value": 20,
              "unit": "mg"
            }
          ]
        },
        {
          "name": "banana",
          "quantity": {
            "value": 1,
            "unit": "medium"
          },
          "calories": 105,
          "macronutrients": {
            "protein": {
              "value": 1.3,
              "unit": "g"
            },
            "carbohydrates": {
              "value": 27,
              "unit": "g"
            },
            "fat": {
              "value": 0.4,
              "unit": "g"
            },
            "fiber": {
              "value": 3.1,
              "unit": "g"
            }
          }
        }
      ],
      "total_calories": 255,
      "water_intake": {
        "value": 250,
        "unit": "ml"
      },
      "consumed_at": new Date("2025-04-20T07:30:00Z"),
      "location": {
        "type": "Point",
        "coordinates": [-73.9857, 40.7484]
      },
      "notes": "Quick breakfast after morning run",
      "tags": ["post-workout", "healthy"],
      "created_at": new Date("2025-04-20T07:35:00Z"),
      "updated_at": new Date("2025-04-20T07:35:00Z")
    });

    // Insert sample sleep record
    await db.collection("sleep_records").insertOne({
      "_id": new ObjectId(),
      "user_id": userId,
      "start_time": new Date("2025-04-19T22:30:00Z"),
      "end_time": new Date("2025-04-20T06:00:00Z"),
      "duration": {
        "value": 450,
        "unit": "minutes"
      },
      "quality": 85,
      "stages": [
        {
          "stage": "light",
          "start_time": new Date("2025-04-19T22:30:00Z"),
          "end_time": new Date("2025-04-19T23:15:00Z"),
          "duration": {
            "value": 45,
            "unit": "minutes"
          }
        },
        {
          "stage": "deep",
          "start_time": new Date("2025-04-19T23:15:00Z"),
          "end_time": new Date("2025-04-20T00:45:00Z"),
          "duration": {
            "value": 90,
            "unit": "minutes"
          }
        },
        {
          "stage": "rem",
          "start_time": new Date("2025-04-20T00:45:00Z"),
          "end_time": new Date("2025-04-20T02:15:00Z"),
          "duration": {
            "value": 90,
            "unit": "minutes"
          }
        },
        {
          "stage": "light",
          "start_time": new Date("2025-04-20T02:15:00Z"),
          "end_time": new Date("2025-04-20T03:00:00Z"),
          "duration": {
            "value": 45,
            "unit": "minutes"
          }
        },
        {
          "stage": "deep",
          "start_time": new Date("2025-04-20T03:00:00Z"),
          "end_time": new Date("2025-04-20T04:30:00Z"),
          "duration": {
            "value": 90,
            "unit": "minutes"
          }
        },
        {
          "stage": "light",
          "start_time": new Date("2025-04-20T04:30:00Z"),
          "end_time": new Date("2025-04-20T06:00:00Z"),
          "duration": {
            "value": 90,
            "unit": "minutes"
          }
        }
      ],
      "interruptions": [
        {
          "start_time": new Date("2025-04-20T02:10:00Z"),
          "end_time": new Date("2025-04-20T02:15:00Z"),
          "duration": {
            "value": 5,
            "unit": "minutes"
          }
        }
      ],
      "heart_rate": {
        "average": 58,
        "min": 52,
        "max": 68
      },
      "respiratory_rate": {
        "average": 14,
        "unit": "breaths_per_minute"
      },
      "environment": {
        "temperature": {
          "value": 19.5,
          "unit": "celsius"
        },
        "humidity": 45,
        "noise_level": {
          "value": 28,
          "unit": "db"
        }
      },
      "device_id": "oura_ring_gen3",
      "notes": "Slept well after evening yoga",
      "tags": ["weekend", "post-exercise"],
      "created_at": new Date("2025-04-20T06:05:00Z"),
      "updated_at": new Date("2025-04-20T06:05:00Z")
    });

    // Insert sample goal
    await db.collection("goals").insertOne({
      "_id": goalId,
      "user_id": userId,
      "title": "Lose 5kg in 3 months",
      "description": "Gradual weight loss through diet and exercise",
      "type": "weight_loss",
      "target": {
        "metric": "weight",
        "start_value": 75,
        "target_value": 70,
        "unit": "kg"
      },
      "timeframe": {
        "start_date": new Date("2025-01-01T00:00:00Z"),
        "target_date": new Date("2025-04-01T00:00:00Z")
      },
      "progress": {
        "current_value": 72.5,
        "percentage": 50,
        "last_updated": new Date("2025-02-15T08:00:00Z")
      },
      "milestones": [
        {
          "value": 74,
          "achieved_at": new Date("2025-01-15T00:00:00Z"),
          "notes": "First milestone achieved!"
        },
        {
          "value": 73,
          "achieved_at": new Date("2025-01-30T00:00:00Z"),
          "notes": "On track with the plan"
        },
        {
          "value": 72,
          "achieved_at": new Date("2025-02-15T00:00:00Z"),
          "notes": "Halfway to goal!"
        }
      ],
      "status": "in_progress",
      "visibility": "private",
      "reminders": [
        {
          "frequency": "daily",
          "time": "08:00:00",
          "enabled": true
        }
      ],
      "created_at": new Date("2024-12-31T10:15:00Z"),
      "updated_at": new Date("2025-02-15T08:05:00Z")
    });

    console.log("Sample data inserted successfully");
    await client.close();
  } catch (error) {
    console.error("Error inserting sample data:", error);
  }
}

// Run the function
insertSampleData();
