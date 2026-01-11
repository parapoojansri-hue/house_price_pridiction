import pandas as pd
import random

def generate():
    # -------------------------
    # 1. Load Data
    # -------------------------
    try:
        sections = pd.read_csv('sections.csv')
        courses = pd.read_csv('courses.csv')
        faculty = pd.read_csv('faculty.csv')
    except FileNotFoundError:
        print("❌ Error: Missing input CSV files (sections.csv, courses.csv, faculty.csv).")
        return

    # Ensure 'subjects' column exists and is a list
    faculty['subject_list'] = faculty['subjects'].apply(lambda x: [s.strip() for s in str(x).split(',')])

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods_per_day = 8
    
    timetable = []
    
    # Track faculty assignments: {faculty_id: {day: [hours_assigned]}}
    faculty_schedule = {row['faculty_id']: {day: [] for day in days} for _, row in faculty.iterrows()}

    # -------------------------
    # 2. Generate for ALL Sections
    # -------------------------
    for _, section in sections.iterrows():
        section_id = section['section_id']
        section_name = section['section_name']
        print(f"Processing Section: {section_name}...")

        # Reset course hours requirement for this section
        # We create a working copy of hours needed per course
        course_needs = []
        for _, c in courses.iterrows():
            course_needs.append({
                'name': c['course_name'],
                'lecture': c.get('lecture_hours', 0),
                'practical': c.get('practical_hours', 0),
                'tutorial': c.get('tutorial_hours', 0)
            })

        for day_idx, day in enumerate(days):
            periods = [None] * periods_per_day
            
            # --- A. Assign Practicals (2 Hour Blocks) ---
            random.shuffle(course_needs) # Randomize order
            for course in course_needs:
                if course['practical'] > 0:
                    # Find a teacher
                    eligible_fac = faculty[faculty['subject_list'].apply(lambda x: course['name'] in x)]
                    
                    for p in range(periods_per_day - 1): # -1 because we need 2 slots
                        if periods[p] is None and periods[p+1] is None:
                            # Check teacher availability
                            for _, fac in eligible_fac.iterrows():
                                f_id = fac['faculty_id']
                                if p not in faculty_schedule[f_id][day] and (p+1) not in faculty_schedule[f_id][day]:
                                    # Assign
                                    for offset in range(2):
                                        periods[p+offset] = {
                                            'section_id': section_id, 'section_name': section_name,
                                            'day': day_idx+1, 'hour': p+offset+1,
                                            'course_name': f"{course['name']} (Lab)",
                                            'faculty_id': f_id, 'name': fac['name']
                                        }
                                        faculty_schedule[f_id][day].append(p+offset)
                                    course['practical'] -= 1
                                    break # Stop looking for teacher
                            if periods[p] is not None: break # Subject assigned, move to next subject

            # --- B. Assign Lectures & Tutorials (1 Hour Blocks) ---
            for course in course_needs:
                # Combine lecture and tutorial needs into single blocks
                hours_needed = course['lecture'] + course['tutorial']
                if hours_needed > 0:
                    eligible_fac = faculty[faculty['subject_list'].apply(lambda x: course['name'] in x)]
                    
                    for _ in range(hours_needed): # Try to fit all hours
                        for p in range(periods_per_day):
                            if periods[p] is None:
                                # Constraint: Don't put same subject twice in a day if possible (optional)
                                if any(p_entry and course['name'] in p_entry['course_name'] for p_entry in periods):
                                     continue 

                                for _, fac in eligible_fac.iterrows():
                                    f_id = fac['faculty_id']
                                    if p not in faculty_schedule[f_id][day]:
                                        periods[p] = {
                                            'section_id': section_id, 'section_name': section_name,
                                            'day': day_idx+1, 'hour': p+1,
                                            'course_name': f"{course['name']} (Lec)",
                                            'faculty_id': f_id, 'name': fac['name']
                                        }
                                        faculty_schedule[f_id][day].append(p)
                                        if course['lecture'] > 0: course['lecture'] -= 1
                                        else: course['tutorial'] -= 1
                                        break
                                if periods[p] is not None: break

            # --- C. Fill Remaining with Library ---
            for p in range(periods_per_day):
                if periods[p] is None:
                    periods[p] = {
                        'section_id': section_id, 'section_name': section_name,
                        'day': day_idx+1, 'hour': p+1,
                        'course_name': 'Library',
                        'faculty_id': 0, 'name': '-'
                    }

            timetable.extend(periods)

    # -------------------------
    # 3. Save
    # -------------------------
    pd.DataFrame(timetable).to_csv('schedule.csv', index=False)
    print("✅ schedule.csv generated successfully!")

if __name__ == "__main__":
    generate()
