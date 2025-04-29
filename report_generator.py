import io
import base64
import datetime
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
from flask import render_template, make_response
import jinja2

class ReportGenerator:
    def __init__(self, user_id, database):
        self.user_id = ObjectId(user_id)
        self.db = database
        self.user = self.db.users.find_one({"_id": self.user_id})
        if not self.user:
            raise ValueError("User not found")
            
    def generate_report(self, report_type, start_date, end_date, metrics):
        """Generate an HTML report directly"""
        # Validate dates
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj > end_date_obj:
            raise ValueError("Start date must be before end date")
            
        # Gather data for the report
        data = {}
        
        # Collect data for selected metrics
        if "sleep" in metrics:
            data["sleep"] = self._get_sleep_data(start_date, end_date)
            
        if "nutrition" in metrics:
            data["nutrition"] = self._get_nutrition_data(start_date, end_date)
            
        if "exercise" in metrics:
            data["exercise"] = self._get_exercise_data(start_date, end_date)
            
        # Generate charts
        charts = self._generate_charts(data, metrics)
        
        # Generate insights
        insights = self._generate_insights(data, metrics)
        
        # Create report HTML
        html_content = render_template(
            "report_template.html",
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            user=self.user,
            data=data,
            charts=charts,
            insights=insights,
            now=datetime.datetime.now
        )
        
        # Save report metadata to database (just metadata, not the actual report)
        report_id = self._save_report_metadata(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )
        
        return html_content, f"health_report_{start_date}_to_{end_date}.html"
        
    def _get_sleep_data(self, start_date, end_date):
        """Retrieve sleep logs from database"""
        sleep_data = list(self.db.sleep_logs.find({
            "user_id": self.user_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("date", 1))
        
        return sleep_data
    
    def _get_nutrition_data(self, start_date, end_date):
        """Retrieve nutrition logs from database"""
        nutrition_data = list(self.db.nutrition_logs.find({
            "user_id": self.user_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("date", 1))
        
        return nutrition_data
    
    def _get_exercise_data(self, start_date, end_date):
        """Retrieve exercise logs from database"""
        exercise_data = list(self.db.exercise_logs.find({
            "user_id": self.user_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("date", 1))
        
        return exercise_data
    
    def _generate_charts(self, data, metrics):
        """Generate base64-encoded charts for the report"""
        charts = {}
        
        # Sleep chart
        if "sleep" in metrics and data.get("sleep"):
            sleep_chart = self._create_sleep_chart(data["sleep"])
            charts["sleep"] = sleep_chart
            
        # Nutrition chart
        if "nutrition" in metrics and data.get("nutrition"):
            nutrition_chart = self._create_nutrition_chart(data["nutrition"])
            charts["nutrition"] = nutrition_chart
            
        # Exercise chart
        if "exercise" in metrics and data.get("exercise"):
            exercise_chart = self._create_exercise_chart(data["exercise"])
            charts["exercise"] = exercise_chart
            
        return charts
    
    def _create_sleep_chart(self, sleep_data):
        """Create sleep chart"""
        # Extract data
        dates = [entry["date"] for entry in sleep_data]
        hours = [entry["hours_slept"] for entry in sleep_data]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.bar(dates, hours, color='#3498db')
        plt.axhline(y=8, color='r', linestyle='-', alpha=0.3)
        plt.title('Sleep Duration by Date', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Hours Slept', fontsize=12)
        plt.ylim(0, 12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Convert plot to base64 image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        encoded = base64.b64encode(image_png).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    
    def _create_nutrition_chart(self, nutrition_data):
        """Create nutrition macronutrient chart"""
        # Calculate average macronutrient distribution
        total_carbs = sum(entry["carbs"] for entry in nutrition_data)
        total_fats = sum(entry["fats"] for entry in nutrition_data)
        total_proteins = sum(entry["proteins"] for entry in nutrition_data)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        if total_carbs == 0 and total_fats == 0 and total_proteins == 0:
            plt.text(0.5, 0.5, 'No nutrition data available', 
                     horizontalalignment='center', fontsize=16, transform=plt.gca().transAxes)
        else:
            labels = ['Carbs', 'Fats', 'Proteins']
            sizes = [total_carbs, total_fats, total_proteins]
            colors = ['#3498db', '#e74c3c', '#2ecc71']
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Macronutrient Distribution', fontsize=16)
            plt.axis('equal')
        
        # Convert plot to base64 image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        encoded = base64.b64encode(image_png).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    
    def _create_exercise_chart(self, exercise_data):
        """Create exercise summary chart"""
        # Group by exercise type
        exercise_types = {}
        for entry in exercise_data:
            exercise_type = entry["exercise_type"]
            if exercise_type not in exercise_types:
                exercise_types[exercise_type] = 0
            exercise_types[exercise_type] += entry["duration"]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        if not exercise_types:
            plt.text(0.5, 0.5, 'No exercise data available', 
                     horizontalalignment='center', fontsize=16, transform=plt.gca().transAxes)
        else:
            types = list(exercise_types.keys())
            durations = list(exercise_types.values())
            
            plt.bar(types, durations, color='#2ecc71')
            plt.title('Exercise Duration by Type', fontsize=16)
            plt.xlabel('Exercise Type', fontsize=12)
            plt.ylabel('Total Duration (minutes)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            plt.xticks(rotation=45)
            plt.tight_layout()
        
        # Convert plot to base64 image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        encoded = base64.b64encode(image_png).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    
    def _generate_insights(self, data, metrics):
        """Generate insights based on the data"""
        insights = []
        
        # Sleep insights
        if "sleep" in metrics and data.get("sleep"):
            sleep_data = data["sleep"]
            if sleep_data:
                avg_duration = sum(entry["hours_slept"] for entry in sleep_data) / len(sleep_data)
                
                if avg_duration < 7:
                    insights.append({
                        "category": "sleep",
                        "title": "Sleep Duration Below Recommended",
                        "description": f"Your average sleep duration is {avg_duration:.1f} hours, which is below the recommended 7-9 hours."
                    })
                elif avg_duration >= 7:
                    insights.append({
                        "category": "sleep",
                        "title": "Healthy Sleep Duration",
                        "description": f"Your average sleep duration is {avg_duration:.1f} hours, which meets the recommended 7-9 hours."
                    })
        
        # Nutrition insights
        if "nutrition" in metrics and data.get("nutrition"):
            nutrition_data = data["nutrition"]
            if nutrition_data:
                balanced_count = sum(1 for entry in nutrition_data if entry.get("balanced", False))
                balanced_percentage = (balanced_count / len(nutrition_data)) * 100
                
                if balanced_percentage < 50:
                    insights.append({
                        "category": "nutrition",
                        "title": "Macronutrient Balance",
                        "description": f"Only {balanced_percentage:.1f}% of your meals have a balanced macronutrient distribution. Consider adjusting your diet."
                    })
                else:
                    insights.append({
                        "category": "nutrition",
                        "title": "Good Macronutrient Balance",
                        "description": f"{balanced_percentage:.1f}% of your meals have a balanced macronutrient distribution. Great job!"
                    })
        
        # Exercise insights
        if "exercise" in metrics and data.get("exercise"):
            exercise_data = data["exercise"]
            if exercise_data:
                total_duration = sum(entry["duration"] for entry in exercise_data)
                exercise_days = len(set(entry["date"] for entry in exercise_data))
                date_range = self._date_range_days(data["exercise"][0]["date"], data["exercise"][-1]["date"])
                
                if date_range > 0:
                    exercise_frequency = (exercise_days / date_range) * 100
                    
                    if exercise_frequency < 40:
                        insights.append({
                            "category": "exercise",
                            "title": "Exercise Frequency",
                            "description": f"You exercised on {exercise_frequency:.1f}% of days. Try to increase to at least 4-5 days per week."
                        })
                    else:
                        insights.append({
                            "category": "exercise",
                            "title": "Good Exercise Frequency",
                            "description": f"You exercised on {exercise_frequency:.1f}% of days. Keep up the good work!"
                        })
        
        return insights
    
    def _date_range_days(self, start_date, end_date):
        """Calculate the number of days between two dates"""
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        return (end - start).days + 1
    
    def _save_report_metadata(self, report_type, start_date, end_date, metrics):
        """Save report metadata to database"""
        report_data = {
            "user_id": self.user_id,
            "title": f"{report_type.title()} Health Report {start_date} to {end_date}",
            "type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "metrics": metrics,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        
        result = self.db.reports.insert_one(report_data)
        return result.inserted_id
    
    def get_user_reports(self, limit=10, skip=0):
        """Get list of reports for the user"""
        reports = list(self.db.reports.find(
            {"user_id": self.user_id}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        return reports
    
    def get_report_by_id(self, report_id):
        """Get report by ID and regenerate it"""
        report_metadata = self.db.reports.find_one({
            "_id": ObjectId(report_id), 
            "user_id": self.user_id
        })
        
        if not report_metadata:
            raise ValueError("Report not found")
            
        # Regenerate the report using stored metadata
        html_content, filename = self.generate_report(
            report_type=report_metadata["type"],
            start_date=report_metadata["start_date"],
            end_date=report_metadata["end_date"],
            metrics=report_metadata["metrics"]
        )
        
        return html_content, filename
