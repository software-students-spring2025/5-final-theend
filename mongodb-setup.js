const mongo = require('mongodb').MongoClient;
const uri = "mongodb+srv://tm3995:<db_password>@healthtracker.vc6hwcx.mongodb.net/?retryWrites=true&w=majority&appName=HealthTracker";
async function setupDatabase() {
  try {
    const client = await mongo.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });
    console.log("Connected to MongoDB Atlas");

    const db = client.db("health_metrics_tracker");
    await db.createCollection("users");
    await db.createCollection("health_metrics");
    await db.createCollection("activities");
    await db.createCollection("nutrition_logs");
    await db.createCollection("sleep_records");
    await db.createCollection("goals");
    await db.createCollection("notifications");
    await db.createCollection("devices");
    await db.createCollection("insights");
    await db.createCollection("reports");

    console.log("Collections created successfully");
    await db.collection("users").createIndex({ "username": 1 }, { unique: true });
    await db.collection("users").createIndex({ "email": 1 }, { unique: true });
    await db.collection("health_metrics").createIndex({ "user_id": 1, "metric_type": 1, "recorded_at": -1 });
    await db.collection("health_metrics").createIndex({ "location": "2dsphere" });
    await db.collection("activities").createIndex({ "user_id": 1, "start_time": -1 });
    await db.collection("activities").createIndex({ "user_id": 1, "activity_type": 1 });
    await db.collection("activities").createIndex({ "location.start": "2dsphere" });
    await db.collection("nutrition_logs").createIndex({ "user_id": 1, "consumed_at": -1 });
    
    // Sleep records indexes
    await db.collection("sleep_records").createIndex({ "user_id": 1, "start_time": -1 });
    
    await db.collection("goals").createIndex({ "user_id": 1, "status": 1 });
    await db.collection("goals").createIndex({ "user_id": 1, "timeframe.target_date": 1 });
    
    await db.collection("notifications").createIndex({ "user_id": 1, "status": 1, "created_at": -1 });
    
    await db.collection("devices").createIndex({ "user_id": 1 });
    await db.collection("devices").createIndex({ "serial_number": 1 }, { unique: true });
    
    await db.collection("insights").createIndex({ "user_id": 1, "created_at": -1 });
    
    await db.collection("reports").createIndex({ "user_id": 1, "period.start": -1 });

    console.log("Indexes created successfully");

    await client.close();
    console.log("MongoDB Atlas setup completed successfully");
  } catch (error) {
    console.error("Error setting up MongoDB Atlas:", error);
  }
}

setupDatabase();
