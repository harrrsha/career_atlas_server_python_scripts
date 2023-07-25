import os
import urllib
from datetime import timedelta
import json
import requests
from dotenv import load_dotenv
#load_dotenv()

def pdf_gen(data,ENVIRONMENT):
    import base64

    from io import BytesIO
    import warnings
    warnings.filterwarnings("ignore")
    import re
    from io import BytesIO
    from datetime import datetime
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.colors import Color
    from reportlab.platypus import Paragraph
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors, styles
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.colors import Color
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import Image
    from reportlab.platypus import Table, TableStyle
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.lib.units import mm
    from datetime import datetime, timedelta
    import pytz

    if ENVIRONMENT == 'qa':
        load_dotenv('.env.qa')
    elif ENVIRONMENT == 'prod':
        load_dotenv('.env.prod')
    elif ENVIRONMENT == 'pre_prod':
        load_dotenv('.env.pre_prod')

    my_dict = data['interviewFeedback']
    group_dict = data['group']
    snapshot_path = os.getenv('SNAPSHOT_PATH')
    resume_parser_path = os.getenv('RESUME_PARSER_PATH')
    org_path = os.getenv('ORG_PATH')
    app_url = os.getenv('APP_URL')
    snap_prefix = app_url + snapshot_path
    import re
    from datetime import datetime

    def is_image_url(url):
        try:
            response = requests.head(url)
            content_type = response.headers['Content-Type']
        except requests.exceptions.RequestException:
            return False
        return content_type.startswith('image/')

    # Access dictionary keys with exception handling
    try:
        first = my_dict['jobId']['title']
    except KeyError:
        first = " "

    try:
        job_code = my_dict['jobId']['code']['jobCode']
    except KeyError:
        job_code = " "

    try:
        snap_img = snap_prefix + my_dict['feedbackId']['snapshots'][0]
        if is_image_url(snap_img):
            pass
        else:
            snap_img = None

    except (KeyError, IndexError):
        snap_img = None

    try:
        organization_logo = app_url + org_path + group_dict['logo']
        if is_image_url(organization_logo):
            pass
        else:
            organization_logo = None

    except KeyError:
        organization_logo = None

    try:
        organization_name = group_dict['name']
    except KeyError:
        organization_name = ""

    try:
        snap_images = []
        for i in my_dict['feedbackId']['snapshots']:
            if is_image_url(snap_prefix + i):
                snap_images.append(snap_prefix + i)
            else:
                pass
    except (KeyError, IndexError):
        snap_images = []

    try:
        status = my_dict['feedbackId']['jobStatus']['title']
    except KeyError:
        status = ""

    try:
        name = [my_dict['candidateId']['firstName'], my_dict['candidateId']['lastName']]
        name = ' '.join(name)
    except KeyError:
        name = ""

    try:
        interviewer_name = [my_dict['primaryInterviewer']['firstName'], my_dict['primaryInterviewer']['lastName']]
        interviewer_name = ' '.join(interviewer_name)
    except KeyError:
        interviewer_name = " "

    # Define the global variable
    global experience
    try:
        experience = round(my_dict['candidateId']['totalExperience'], 0)
    except KeyError:
        experience = 0  # Default value if key is missing

    try:
        current_company = my_dict['candidateId']['experience'][0]['company']
        if current_company == None:
            current_company = "  "
    except (KeyError, IndexError):
        current_company = ""  # Default value if key or index is missing

    try:
        interview_level = my_dict['round']
    except KeyError:
        interview_level = ""

    try:
        interview_mode = my_dict['mode']
    except KeyError:
        interview_mode = ""

    global int_duration
    try:
        int_duration = my_dict['slotDuration']
    except KeyError:
        int_duration = ""

    try:
    	intv_start_raw_output = my_dict['scheduleStartDate']
    	date_time_obj = datetime.strptime(intv_start_raw_output, '%Y-%m-%dT%H:%M:%S.%fZ')
    	utc_timezone = pytz.timezone('UTC')
    	ist_timezone = pytz.timezone('Asia/Kolkata')
    	interview_start_datetime = utc_timezone.localize(date_time_obj)  # Set input as UTC timezone aware
    	interview_start_datetime_ist = interview_start_datetime.astimezone(ist_timezone)  # Convert to IST
    	interview_start_date_time = interview_start_datetime_ist.strftime('%d %b %Y | %I:%M %p')
        
    except (KeyError, ValueError):
    	interview_start_date_time = ""

    try:
        overall_comments = my_dict['feedbackId']['overallComment']
        output_str = re.sub('<[^<]+?>', '', overall_comments)
    except KeyError:
        overall_comments = ""

    try:
        video_link = my_dict['feedbackId']['recordingLinks']
    except KeyError:
        video_link = ""

    try:
        candidate_name = [my_dict['candidateId']['firstName'], my_dict['candidateId']['lastName']]
    except KeyError:
        candidate_name = ["", ""]

    try:
        email_id = my_dict['candidateId']['emailId']
    except KeyError:
        email_id = ""

    try:
        job_details = my_dict['jobId']['title'], my_dict['jobId']['code']['jobCode']
        job_details = ' '.join(job_details)
    except KeyError:
        job_details = ""


    if int_duration and interview_start_date_time:
        interview_start_datetime = datetime.strptime(interview_start_date_time, '%d %b %Y | %I:%M %p')
        interview_start_datetime = pytz.timezone('UTC').localize(
            interview_start_datetime)  # Set input as UTC timezone aware
        interview_end_datetime = interview_start_datetime + timedelta(minutes=int(int_duration))
        interview_end_datetime_ist = interview_end_datetime.astimezone(pytz.timezone('Asia/Kolkata'))  # Convert to IST
        interview_end_time = interview_end_datetime_ist.strftime('%d %b %Y | %I:%M %p')
    else:
        interview_end_time = ""

    combined_text = job_code + "  |  " + first + "  |  " + interview_level + " Interview"
    req_job = first + " | " + job_code
    name_exp = name + " | " + str(experience) + " Years"

    pdfmetrics.registerFont(TTFont('Roboto-Medium', os.getenv("ASSET")+'font/Roboto-Medium.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto-Light', os.getenv("ASSET")+'font/Roboto-Light.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', os.getenv("ASSET")+'font/Roboto-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto', os.getenv("ASSET")+'font/Roboto-Black.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto-Regular', os.getenv("ASSET")+'font/Roboto-Regular.ttf'))

    child_technical_skills = []
    parent_technical_skills = []
    for topic in my_dict['feedbackId']['skills']:
        parent_id = ""
        parent_title = ""
        sub_skill_title = ""
        rating = ""
        comments = ""

        if topic.get('name', {}).get('parent'):
            try:
                parent_id = topic['name']['parent']['_id']
            except KeyError:
                pass

            try:
                parent_title = topic['name']['parent']['title']
            except KeyError:
                pass

            try:
                sub_skill_title = topic['name']['title']
            except KeyError:
                pass

            try:
                rating = topic['rating']
            except KeyError:
                pass

            try:
                comments = topic['comment']
            except KeyError:
                pass

            for question in topic['questions']:
                questions = ""
                q_rating = ""
                q_feedback = ""

                try:
                    questions = question['question']['title']
                except KeyError:
                    pass

                try:
                    q_rating = question['answer']
                except KeyError:
                    pass

                try:
                    q_feedback = question['comment']
                except KeyError:
                    pass

                child_technical_skills.append({
                    'parent_id': parent_id,
                    'parent_title': parent_title,
                    'sub_skill_title': sub_skill_title,
                    'rating': rating,
                    'comments': comments,
                    'questions': questions,
                    'q_rating': q_rating,
                    'q_feedback': q_feedback
                })

        else:
            try:
                sub_skill_title = topic['name']['title']
            except KeyError:
                pass

            try:
                rating = topic['rating']
            except KeyError:
                pass

            try:
                comments = topic['comment']
            except KeyError:
                pass

            for question in topic['questions']:
                questions = ""
                q_rating = ""
                q_feedback = ""

                try:
                    questions = question['question']['title']
                except KeyError:
                    pass

                try:
                    q_rating = question['answer']
                except KeyError:
                    pass

                try:
                    q_feedback = question['comment']
                except KeyError:
                    pass

                parent_technical_skills.append({
                    'sub_skill_title': sub_skill_title,
                    'rating': rating,
                    'comments': comments,
                    'questions': questions,
                    'q_rating': q_rating,
                    'q_feedback': q_feedback
                })

    # Define data for table
    tech_table_data = [['Skills', 'Sub Skills', 'Rating', 'Feedback']]

    # Group skills by parent and child
    parent_skills = {}
    child_skills = {}
    primary_skills = []
    for topic in my_dict['feedbackId']['skills']:
        if topic.get('name', {}).get('parent'):
            parent_title = topic['name']['parent']['title']
            child_title = topic['name']['title']
            rating = topic['rating']
            comment = topic['comment']
            if parent_title not in parent_skills:
                parent_skills[parent_title] = []
            parent_skills[parent_title].append((child_title, rating, comment))
        elif topic.get('name', {}).get('title'):
            child_title = topic['name']['title']
            rating = topic['rating']
            comment = topic['comment']
            if child_title not in child_skills:
                child_skills[child_title] = []
            child_skills[child_title].append((rating, comment))
        else:
            primary_title = topic['name']['primaryTitle']
            rating = topic['rating']
            comment = topic['comment']
            primary_skills.append((primary_title, rating, comment))

    def rating_to_stars(rating):
        circle_size = 15  # adjust as per requirement
        filled_color = Color(1.0, 0.843, 0.0)  # adjust as per requirement
        empty_color = Color(211 / 255, 211 / 255, 211 / 255)  # adjust as per requirement
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        circle_html = ""
        for i in range(5):
            if i < rating:
                circle_html += '<font size="{}" color="{}">&#9733;</font> '.format(circle_size, filled_color)
            else:
                circle_html += '<font size="{}" color="{}">&#9733;</font> '.format(circle_size, empty_color)
        return circle_html.strip()

    # Build the tech table
    for parent_title, child_tuples in parent_skills.items():
        row_added = False
        for child_tuple in child_tuples:
            child_title, rating, comment = child_tuple
            p_rating_circles = Paragraph(rating_to_stars(int(child_skills[parent_title][0][0])))
            if not row_added:
                tech_table_data.append(
                    [parent_title, '', p_rating_circles, child_skills[parent_title][0][1]])
                row_added = True
            # Replace rating with circles
            styles = getSampleStyleSheet()
            rating_circles = Paragraph(rating_to_stars(int(rating)), styles['Normal'])

            tech_table_data.append(['', child_title, rating_circles, comment])

    for primary_tuple in primary_skills:
        primary_title, rating, comment = primary_tuple
        # Replace rating with circles
        styles = getSampleStyleSheet()
        rating_circles = Paragraph(rating_to_stars(int(rating)), styles['Normal'])
        tech_table_data.append([primary_title, '', rating_circles, comment])

    for child_title, child_tuples in child_skills.items():
        if child_title not in parent_skills.keys():
            for child_tuple in child_tuples:
                rating, comment = child_tuple
                # Replace rating with circles
                styles = getSampleStyleSheet()
                rating_circles = Paragraph(rating_to_stars(int(rating)), styles['Normal'])
                tech_table_data.append([child_title, '', rating_circles, comment])

    # Create technical skills table
    header_row_height = 0.4 * inch
    data_row_height = 0.36 * inch
    row_heights = [header_row_height] + [data_row_height] * (len(tech_table_data) - 1)

    primary_skills = list(set(parent_skills.keys()) | set(child_skills.keys()))


    header_text = job_code + "  |  " + first + "  |  " + interview_level + " Interview"
    footer_text_a = "Powered by : "
    greyish_blue_color = Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
    def add_header(pdf_canvas):
        header_color = greyish_blue_color
        # Draw the header on every page
        pdf_canvas.saveState()
        pdf_canvas.setFillColor(header_color)
        pdf_canvas.rect(0, letter[1] - 0.55 * inch, letter[0], 0.8 * inch, stroke=0, fill=1)
        pdf_canvas.restoreState()
        if organization_logo == None:
            pdf_canvas.setFillColorRGB(0.5, 0.5, 0.5, alpha=1)
            pdf_canvas.setFont('Roboto-Medium', 12)
            pdf_canvas.drawString(23, letter[0] + 2.15 * inch, organization_name)
        else:
            pdf_canvas.drawImage(organization_logo, 5, letter[0]+ 2 * inch , width=1.5 * inch, height=0.4 * inch, preserveAspectRatio=True, mask='auto')

        pdf_canvas.setFillColor(Color(0.3, 0.3, 0.3))
        pdf_canvas.setFont('Roboto-Regular', 11)
        # Calculate the width of the text string
        text_width_h = pdf_canvas.stringWidth(header_text)
        # Calculate the x coordinate where the text should end
        right_margin_x = 617  # Replace with the x-coordinate of the right edge of the visible area
        end_x = right_margin_x - 28  # Subtract the desired margin from the right edge
        start_x = end_x - text_width_h
        pdf_canvas.drawString(start_x, letter[1] - 0.31 * inch, header_text)

    def add_footer(pdf_canvas):
        # Draw the footer on every page
        footer_color = greyish_blue_color
        pdf_canvas.saveState()
        pdf_canvas.setFillColor(footer_color)
        pdf_canvas.rect(0, 0, letter[0], 0.4 * inch, stroke=0, fill=1)
        pdf_canvas.restoreState()

        cur_page_num = pdf_canvas.getPageNumber()
        pagett = "Page %s" % cur_page_num
        pdf_canvas.drawString(20, letter[0] - 8.35 * inch, pagett)

        pdf_canvas.drawString(429, letter[0] - 8.35 * inch, footer_text_a)
        pdf_canvas.setFillColorRGB(0.3, 0.3, 0.6)  # blue color
        footer_text_b = "www.careeratlas.in"
        pdf_canvas.drawString(495, letter[0] - 8.35 * inch, footer_text_b)

    # Create the table
    export_filename = "interview_feedback_"+my_dict['_id']+".pdf"     
    pdf_canvas = canvas.Canvas(os.getenv('RESUME_PARSER_PATH')+export_filename, pagesize=letter)
    x1 = 30
    y1 = 755

    add_header(pdf_canvas)
    add_footer(pdf_canvas)
    # set the fill color to a shade of grey with low alpha value
    pdf_canvas.setFillColorRGB(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
    # pdf_canvas.line(x1, y1 - 360, x1 + 538, y1 - 360)
    # define the rectangle coordinates and dimensions with padding
    padding = 9
    x, y = x1 - 20 + padding, y1 - 180 + padding
    width, height = 590-1.9 * padding, 169 - 2 * padding
    radius = 10

    # draw the rectangle with curved edges
    pdf_canvas.roundRect(x, y, width, height, radius, stroke=0, fill=1)

    # print "Feedback Form" in darker shade of grey and larger font size with padding
    pdf_canvas.setFillColorRGB(0.5, 0.5, 0.5, alpha=1)
    pdf_canvas.setFont('Roboto-Medium', 12)
    pdf_canvas.drawString(x1 - 7 + padding, y1 - 60 - padding, 'Overall Comments')

    # print the combined text inside the rectangle with larger font size with padding
    pdf_canvas.setFillColorRGB(0.25, 0.25, 0.25, alpha=1)
    pdf_canvas.setFont('Roboto-Bold', 14)
    pdf_canvas.drawString(x + padding + 4, y + height - 17 - padding, name_exp)
    # Set the starting coordinates
    x1 = 34
    y1 = 672
    # Define the maximum width of the text
    max_width = 690
    # Split the text into lines that fit within the maximum width
    overall_comments_lines = []
    line = ''
    for word in output_str.split():
        if pdf_canvas.stringWidth(line + ' ' + word) < max_width:
            line = line + ' ' + word
        else:
            overall_comments_lines.append(line.strip())
            line = word
    if line:
        overall_comments_lines.append(line.strip())
    # Print each line of text
    for line in overall_comments_lines:
        pdf_canvas.setFont('Roboto-Regular', 11)
        pdf_canvas.setFillColor(Color(0.2, 0.2, 0.2))
        pdf_canvas.drawString(x1-1, y1 - 6, line)
        y1 -= 15  # Adjust this value to set the distance between line

    x1 = 30
    y1 = 755
    if status == "Interview - Selected":
        # set fill color to green
        pdf_canvas.setFillColorRGB(0.2, 0.745, 0.624)
    else:
        # set fill color to red
        pdf_canvas.setFillColorRGB(0.863, 0.078, 0.235)
    # define coordinates and dimensions of green box with padding
    box_width, box_height = 137, 26
    box_x = x + width - box_width - padding
    box_y = y + height - box_height - padding

    # draw the green box
    pdf_canvas.roundRect(box_x, box_y, box_width, box_height, 5, stroke=0, fill=1)

    # print the status in white on the green box
    pdf_canvas.setFillColorRGB(1, 1, 1)

    # get the width and height of the status text
    text_width = pdf_canvas.stringWidth(status, 'Roboto-Medium', 9)
    text_height = 9

    # calculate the center coordinates of the box
    center_x = box_x + box_width / 2
    center_y = box_y + box_height / 2

    # adjust the position of the status text to center it in the box with padding
    text_x = (center_x - text_width / 2) - 18
    text_y = (center_y - text_height / 2) + 0.5
    pdf_canvas.setFont('Roboto-Bold', 12.5)
    pdf_canvas.drawString(text_x, text_y, status)
    pdf_canvas.setFillColor(Color(0.25, 0.25, 0.25))
    pdf_canvas.setFont("Roboto-Medium", 13)
    pdf_canvas.drawString(x1, y1 - 200, "CANDIDATE DETAILS: ")

    if snap_img == None:
        pdf_canvas.drawString(x1 + 381, y - 132, "")
    else:
        pdf_canvas.drawImage(snap_img, x1 + 381, y - 132, width=2.45 * inch, height=1.5 * inch)

    pdf_canvas.setFillColor(Color(0.5, 0.5, 0.5))
    pdf_canvas.setFont('Roboto-Regular', 13)
    pdf_canvas.drawString(x1, y1 - 225, "Candidate Name")
    pdf_canvas.drawString(x1 + 170, y1 - 225, 'Email ID')
    pdf_canvas.drawString(x1, y1 - 270, "Experience")
    pdf_canvas.drawString(x1 + 170, y1 - 270, 'Current Company')
    pdf_canvas.drawString(x1, y1 - 312, "Primary Skills:")
    pdf_canvas.setFillColor(Color(0.2, 0.2, 0.2))
    pdf_canvas.setFont('Roboto-Regular', 13)
    pdf_canvas.drawString(x1, y1 - 290, str(experience) + " Years")
    pdf_canvas.drawString(x1 + 170, y1 - 290, current_company)
    pdf_canvas.drawString(x1, y1 - 246, name)
    pdf_canvas.drawString(x1 + 170, y1 - 246, email_id)

    x = x1 + 5
    y = y1 - 349

    def primary_skills_titles(x, y):
        for i, title in enumerate(primary_skills):
            if i > 0:
                pdf_canvas.drawString(x, y, "  |  ")
                x += pdf_canvas.stringWidth("  |  ")
            pdf_canvas.setFont('Roboto-Regular', 12)
            pdf_canvas.setFillColor(Color(0, 0, 0))
            pdf_canvas.drawString(x, y, title)
            x += pdf_canvas.stringWidth(title)


    pdf_canvas.setFillColor(Color(0.12, 0.25, 0.25))

    pdf_canvas.setFont("Roboto-Medium", 13)
    primary_skills_titles(x-5, y+15)
    pdf_canvas.line(x1, y1 - 377, x1 + 543, y1 - 377)
    # set the colors
    grey = Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
    black = (0, 0, 0)
    pdf_canvas.setFillColor(Color(0.25, 0.25, 0.25))
    pdf_canvas.setFont("Roboto-Medium", 13)
    pdf_canvas.drawString(x1 - 1, y1 - 405, "INTERVIEW DETAILS")
    pdf_canvas.setFillColor(Color(0.5, 0.5, 0.5))
    pdf_canvas.setFont('Roboto-Regular', 12)
    pdf_canvas.drawString(x1, y1 - 430, "Interviewer Name")
    pdf_canvas.drawString(x1 + 199, y1 - 430, 'Interview Level')
    pdf_canvas.drawString(x1 + 361, y1 - 430, 'Interview Start Date & Time')
    pdf_canvas.drawString(x1 + 361, y1 - 480, 'Interview Mode')
    pdf_canvas.drawString(x1, y1 - 480, 'Interview End Date & Time')
    pdf_canvas.drawString(x1 + 199, y1 - 480, 'Duration')
    pdf_canvas.drawString(x1, y1 - 532, 'Video Link:  ')
    pdf_canvas.setFillColor(Color(0.2, 0.2, 0.2))
    pdf_canvas.setFont('Roboto-Regular', 13)
    # pdf_canvas.drawString(x1, y1 - 430, overall_comments)
    pdf_canvas.drawString(x1, y1 - 452, interviewer_name)
    pdf_canvas.drawString(x1 + 199, y1 - 502, str(int_duration) + " min")
    pdf_canvas.drawString(x1 + 361, y1 - 502, interview_mode)
    pdf_canvas.drawString(x1, y1 - 502, interview_end_time)
    pdf_canvas.drawString(x1 + 199, y1 - 452, interview_level)
    pdf_canvas.setFillColor(Color(0.3, 0.3, 0.6))
    pdf_canvas.drawString(x1 + 90, y1 - 532, video_link)
    pdf_canvas.setFillColor(Color(0.2, 0.2, 0.2))
    pdf_canvas.drawString(x1 + 360, y1 - 452, interview_start_date_time)
    pdf_canvas.line(x1, y1 - 553, x1 + 543, y1 - 553)
    pdf_canvas.setFillColor(Color(0.25, 0.25, 0.25))
    pdf_canvas.setFont("Roboto-Medium", 13)
    pdf_canvas.drawString(x1, y1 - 582, "JOB DETAILS: ")
    pdf_canvas.setFont('Roboto-Regular', 12)
    pdf_canvas.setFillColor(Color(0.5, 0.5, 0.5))
    pdf_canvas.drawString(x1, y1 - 660, "Must have skills:  ")
    pdf_canvas.drawString(x1, y1 - 610, "Job Title / ID")
    pdf_canvas.drawString(x1 + 276, y1 - 610, "Experience")
    pdf_canvas.setFillColor(Color(0.2, 0.2, 0.2))
    pdf_canvas.setFont('Roboto-Regular', 13)
    pdf_canvas.drawString(x1 + 276, y1 - 632, str(experience) + " Years")
    pdf_canvas.drawString(x1, y1 - 632, req_job)

    # Define the starting coordinates for the first rectangle
    x = x1 + 5
    y = y1 - 705
    pdf_canvas.setFont('Roboto-Medium', 15)
    pdf_canvas.setFillColor(Color(0, 0, 0))
    primary_skills_titles(x-5, y+10)

    pdf_canvas.showPage()

    add_header(pdf_canvas)
    add_footer(pdf_canvas)

    x1 = 40
    y1 = 700
    pdf_canvas.setFont('Roboto-Medium', 15)
    pdf_canvas.setFillColor(Color(0, 0, 0))
    # Declare num_additional_lines as a global variable
    from reportlab.platypus import Table
    from reportlab.lib.units import inch
    num_additional_lines = 0


    import re

    def modify_column_text(table_data, col_num, max_chars):
        special_chars_regex = r'[\W_()\[\]]'  # Regular expression to match special characters including parenthesis and brackets

        for i in range(1, len(table_data)):
            try:
                col_text = table_data[i][col_num]
                if col_text is None:
                    col_text = '-'
            except:
                col_text = ""

            if len(col_text) > max_chars:
                split_text = re.findall('.{1,%d}(?:\W+|$)|\S+?(?=\s+|$)' % max_chars, col_text)
                modified_text = []
                for text in split_text:
                    special_chars = re.findall(special_chars_regex, text)
                    text_len = len(text) - len(special_chars)
                    if text_len > max_chars:
                        text = text[:-text_len + max_chars - len(special_chars)]
                    modified_text.append(text)

                table_data[i][col_num] = '\n'.join(modified_text)

        return table_data

    d_row_height = 0.4 * inch  # Initial row height in inches
    tech_table_data = modify_column_text(tech_table_data, 0, 20)
    tech_table_data = modify_column_text(tech_table_data, 1, 38)
    tech_table_data = modify_column_text(tech_table_data, 3, 35)

    # Calculate the additional lines and increase the row heights accordingly
    for i, row in enumerate(tech_table_data):
        num_additional_lines = row[0].count('\n') + row[1].count('\n') + row[3].count('\n')
        row_heights[i] += num_additional_lines * (0.2 * inch)

    col_widths = [1.73 * inch, 2.67 * inch, 1.2 * inch, 2.36 * inch]
    tst = Table(tech_table_data, colWidths=col_widths, rowHeights=row_heights)

    # Add style to the table
    tst.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)),
        ('FONT SIZE', (0, 0), (-1, 0), 11),
        ('TEXT COLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TOP PADDING', (0, 0), (-1, 0), 14),
        ('FONT NAME', (0, 0), (-1, 0), 'Roboto-Bold'),
        ('FONT SIZE', (0, 0), (-1, 0), 9),
        ('BOTTOM PADDING', (0, 0), (-1, 0), 20),
        ('FONTNAME', (0, 1), (-1, -1), 'Roboto-Regular'),
        ('FONT SIZE', (0, 1), (-1, -1), 9),
        ('TOP PADDING', (0, 1), (-1, -1), 5),
        ('BOTTOM PADDING', (0, -1), (-1, -1), 15),
        ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, Color(0.9, 0.9, 0.9, alpha=1.0)),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('VALIGN', (2, 1), (2, -1), 'MIDDLE'),
        ('TOP PADDING', (2, 1), (2, -1), 1),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('LEFT PADDING', (3, 1), (3, -1), 10 ),
        ('VALIGN', (3, 1), (3, -1), 'MIDDLE'),
        ('LEFT PADDING', (0, 1), (2, -1), 10),
    ]))

    # Alternate row colors
    for i, row in enumerate(tech_table_data):
        if i % 2 != 0:
            bg_color = Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
        else:
            bg_color = colors.white
        tst.setStyle([('BACKGROUND', (0, i + 1), (-1, i + 1), bg_color)])
    pdf_canvas.drawString(22, 720, "Technical Skills Feedback")
    # pdf_canvas.drawString(32, last_string_y,"Soft Skills")
    tst.wrapOn(pdf_canvas, 80, 0)
    tst_height = tst.wrapOn(pdf_canvas, 80, 0)[1]
    tst.drawOn(pdf_canvas, 19, 700 - tst_height)

    soft_skills = []
    styles = getSampleStyleSheet()
    for skill in my_dict['feedbackId']['softSkills']:
        soft_skills.append({
            'skill_title': skill['name'],
            'rating': skill['rating'],
            'comments': skill['comment']
        })
    # Define data for table
    soft_table_data = [['Soft Skills', 'Rating', 'Feedback']]
    for skill in soft_skills:
        rating_stars = Paragraph(rating_to_stars(int(skill['rating'])), styles['Normal'])
        soft_table_data.append([skill['skill_title'], rating_stars, skill['comments']])

    soft_table_data = modify_column_text(soft_table_data, 0, 18)
    soft_table_data = modify_column_text(soft_table_data, 2, 56)

    tst_height = tst.wrapOn(pdf_canvas, 80, 0)[1]
    # pdf_canvas.drawString(x1 - 5, y1 - 300 - tst_height, "Soft Skills")

    row_height = 0.4 * inch
    row_heights = [row_height] * len(soft_table_data)
    # Calculate the additional lines and increase the row heights accordingly
    for i, row in enumerate(soft_table_data):
        num_additional_lines = row[2].count('\n')
        row_heights[i] += num_additional_lines * (0.2 * inch)


    sst = Table(soft_table_data, colWidths=[3.2 * inch, 1.2 * inch, 3.6 * inch], rowHeights=row_heights) #7.97 inch

    sst.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)),
        ('FONT SIZE', (0, 0), (-1, 0), 10),
        ('TEXT COLOR', (0, 0), (-1, 0), colors.black),
        ('TOP PADDING', (0, 0), (-1, 0), 13),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONT NAME', (0, 0), (-1, 0), 'Roboto-Bold'),
        ('BOTTOM PADDING', (0, 0), (-1, 0), 20),
        ('FONTNAME', (0, 1), (-1, -1), 'Roboto-Regular'),
        ('FONT SIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, Color(0.9, 0.9, 0.9, alpha=1.0)),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left align first column
        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),  # Vertically align first column
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),  # Left align third column
        ('VALIGN', (2, 0), (2, -1), 'MIDDLE'),  # Vertically align third column
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Align third column text to the left
        ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),  # Vertically align third column text to the middle
        ('LEFT PADDING', (1, 1), (1, -1), 30),  # Remove top padding for the third column
        ('TOP PADDING', (1, 1), (1, -1), 20),
    ]))

    # alternate row colors
    for i, row in enumerate(soft_table_data[1:], start=1):
        if i % 2 == 0:
            bg_color = Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
        else:
            bg_color = colors.white
        sst.setStyle([('BACKGROUND', (0, i), (-1, i), bg_color)])

    total_page_height = pdf_canvas._pagesize[1]
    header_height = 0.55 * inch
    footer_height = 0.4 * inch
    tst_height = tst.wrapOn(pdf_canvas, 80, 0)[1]  # Replace with the actual height of the tst table
    spacing = 30

    available_space = total_page_height - header_height - footer_height - tst_height - spacing

    sst_height = sst.wrapOn(pdf_canvas, 80, 0)[1]
    req_space = sst_height + 150
    header_height = 50

    # Check if there is enough available space on the current page for the sst table
    if available_space < req_space:
        pdf_canvas.showPage()
        add_header(pdf_canvas)
        add_footer(pdf_canvas)
        y_start = total_page_height - header_height - 20
    else:
        y_start = 700 - tst_height-spacing
        print(y_start+100)

    pdf_canvas.setFillColor(Color(0, 0, 0))
    pdf_canvas.setFont("Roboto-Medium", 15)
    pdf_canvas.drawString(22, y_start + 6, 'Soft Skills')

    # Draw the table on the canvas
    sst.wrapOn(pdf_canvas, 0, 0)
    sst.drawOn(pdf_canvas, 22, y_start - sst_height - 10)

    pdf_canvas.showPage()

    add_header(pdf_canvas)
    add_footer(pdf_canvas)
    x1 = 40
    y1 = 990

    add_header(pdf_canvas)
    add_footer(pdf_canvas)
    pdf_canvas.setFillColor(Color(0, 0, 0))
    pdf_canvas.setFont("Roboto-Medium", 15)
    pdf_canvas.drawString(19, 725, " Interview Questions")
    # Define the data for the table
    q_tables = []
    # Define the amount of space to add before and after the primary skill line
    y_start = 700
    # Initialize a flag to track if a table is being printed on the current page
    table_on_current_page = False

    def rating_To_img(q_rating):
        if q_rating == 1:
            image_path = os.getenv("ASSET") +'image/1-red-wrong.png'
            return Image(image_path, width=cell_width, height=cell_height)  
        elif q_rating == 2:
            image_path = os.getenv("ASSET") +'image/2-yellow-satisf.png'
            return Image(image_path, width=cell_width, height=cell_height)
        elif q_rating == 3:
            image_path = os.getenv("ASSET") +'image/3-green-good.png'
            return Image(image_path, width=cell_width, height=cell_height)
        # Add more rating conditions if needed
        else:
            return None

    # Set the cell width and height for the images
    cell_width = 1 * inch
    cell_height = 0.3 * inch

    # Loop through each primary skill
    pdf_canvas.setFont('Roboto-Medium', 12)

    for primary_skill in primary_skills:
        y_start -= 10
        q_table_data = [['Skill', 'Questions', 'Ratings', 'Comments']]

        for parent_technical_skill in parent_technical_skills:
            if parent_technical_skill['sub_skill_title'] == primary_skill:
                rating_rects = rating_To_img(parent_technical_skill['q_rating'])
                q_table_data.append([parent_technical_skill['sub_skill_title'],
                                     parent_technical_skill['questions'],
                                     rating_rects,
                                     parent_technical_skill['comments']])

        for child_technical_skill in child_technical_skills:
            if child_technical_skill['parent_title'] == primary_skill:
                rating_rects = rating_To_img(child_technical_skill['q_rating'])
                q_table_data.append([child_technical_skill['sub_skill_title'],
                                     child_technical_skill['questions'],
                                     rating_rects,
                                     child_technical_skill['comments']])

        q_table_data = modify_column_text(q_table_data, 0, 25)
        q_table_data = modify_column_text(q_table_data, 1, 42)
        q_table_data = modify_column_text(q_table_data, 3, 30)

        def_h = 0.4 * inch  # Default row height in inches
        line_height = 0.2 * inch  # Height increment for each additional line

        row_heights = [0.4 * inch] * len(q_table_data)  # Initialize the row heights with the default height

        # Calculate the additional lines and increase the row heights accordingly
        for i, row in enumerate(q_table_data):
            num_additional_lines = row[0].count('\n') + row[1].count('\n') + row[3].count('\n')
            row_heights[i] += num_additional_lines * (0.2 * inch)

        # Create th table with the correct row heights
        q_table = Table(q_table_data, colWidths=[2 * inch, 2.8 * inch, 1.1 * inch, 2 * inch], rowHeights=row_heights)
        q_table_data.append(' ')
        # Define the table style
        q_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0),Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONT SIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONT SIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, Color(0.8, 0.8, 0.8, alpha=0.5)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFT PADDING', (0, 0), (0, -1), 6),  # Add left padding to the first column
            ('LEFT PADDING', (1, 0), (1, -1), 6),  # Add left padding to the second column
            ('LEFT PADDING', (3, 0), (3, -1), 6),  # Add left padding to the fourth column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (2, 0), (3, 0), Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)),
            ('TEXTCOLOR', (2, 0), (3, 0), colors.black),
            ('ALIGN', (2, 0), (3, 0), 'LEFT'),
            ('FONT SIZE', (2, 0), (3, 0), 9),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, 1), Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('VALIGN', (2, 1), (2, -1), 'MIDDLE'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('FONT SIZE', (0, 1), (-1, 1), 9),
            ('BOTTOM PADDING', (0, 0), (-1, 0), 0),  # Remove bottom padding of the first row
            ('BOTTOM PADDING', (2, 1), (2, -1), 0),  # Remove bottom padding of the third row
            ('TOP PADDING', (2, 1), (2, -1), 0),  # Remove Top padding of the third row
            ('BOTTOM PADDING', (0, -1), (-1, -1), 0),  # Remove bottom padding of the last row
            ('BOTTOM PADDING', (0, 1), (-1, -1), 0),  # Remove bottom padding of the second row onwards
        ]))

        # Add your code to print the table with modified styles

        # alternate row colors
        for i, row in enumerate(q_table_data[1:], start=1):
            if i % 2 == 0:
                bg_color = Color(0.9607843137254902, 0.9686274509803922, 0.9803921568627451, alpha=1.0)
            else:
                bg_color = colors.white
            q_table.setStyle([('BACKGROUND', (0, i), (-1, i), bg_color)])

        # Add the table to the list of tables
        q_tables.append(q_table)

    # Set the starting point of the first table
    y_start = 687
    # Get the height of the current page
    _, current_page_height = pdf_canvas._pagesize
    # Check if a table is being printed on the current page

    # Loop through each table
    for q_table, primary_skill in zip(q_tables, primary_skills):

        # Get the height of the table
        table_height = q_table.wrapOn(pdf_canvas, 0, 0)[1]
        # If the table went off the bottom of the page, create a new page
        if y_start - table_height < 20:
            pdf_canvas.showPage()
            add_header(pdf_canvas)
            add_footer(pdf_canvas)
            pdf_canvas.setFillColor(Color(0, 0, 0))
            pdf_canvas.setFont("Roboto-Medium", 15)
            pdf_canvas.drawString(18, 720, " Interview Questions")
            y_start = current_page_height - 105
            table_on_current_page = False
        else:
            table_on_current_page = True

        pdf_canvas.setFont('Roboto-Light', 12)
        pdf_canvas.drawString(22, y_start + 6, 'Skill : ')
        pdf_canvas.setFont('Roboto-Medium', 12)
        pdf_canvas.drawString(52, y_start + 6, f'{primary_skill}')
        # Modify content of first column
        for i, row in enumerate(q_table_data[1:], start=1):
            text = row[0]
            col_width = 150  # width of the first column in points
            if pdf_canvas.stringWidth(text, 'Roboto-Regular', 12) > 2.8 * col_width / 72:
                # Split the text into two lines if the length exceeds 2.8 inches
                first_line_len = 0
                first_line = ''
                second_line = ''
                for word in text.split():
                    word_len = pdf_canvas.stringWidth(word, 'Roboto-Regular', 12)
                    if first_line_len + word_len < 2.8 * col_width / 72:
                        first_line += ' ' + word if first_line_len > 0 else word
                        first_line_len += word_len
                    else:
                        second_line += ' ' + word if len(second_line) > 0 else word
                # Add the two lines to the table data
                q_table_data[i][0] = first_line
                q_table_data.insert(i + 1, ['-' + second_line])
        # Draw the table on the canvas
        q_table.wrapOn(pdf_canvas, 0, 0)
        q_table.drawOn(pdf_canvas, 22, y_start - table_height - 10)
        y_start -= table_height + 50

    pdf_canvas.showPage()
    add_header(pdf_canvas)
    add_footer(pdf_canvas)
    # Define the page size and margin
    page_width, page_height = letter
    left_margin = 50
    right_margin = 50
    top_margin = 100
    bottom_margin = 50
    def snap_print(snap_images):
        # Define the number of columns and rows in the grid
        num_columns = 2
        num_rows = 4
        # Calculate the width and height of each grid cell
        cell_width = (page_width - left_margin - right_margin) / num_columns
        cell_height = (page_height - top_margin - bottom_margin) / num_rows
        pdf_canvas.setFont("Roboto-Medium", 15)
        pdf_canvas.setFillColor(Color(0, 0, 0))
        pdf_canvas.drawString(left_margin+12, 715, "Interview Snapshots")
        # Iterate through the images list and position each image in the grid
        for i, image_path in enumerate(snap_images[:8]):
            img_width = cell_width - 20  # Adjust image width as needed
            img_height = cell_height - 20  # Adjust image height as needed
            # Calculate the row and column indices for the current image
            row = i // num_columns
            col = i % num_columns
            # Calculate the position of the current image
            x = left_margin + col * cell_width + 10  # Adjust left margin and spacing as needed
            y = page_height - top_margin - (row + 1) * cell_height + 10  # Adjust top margin and spacing as needed
            # Draw the image on the PDF canvas
            pdf_canvas.drawImage(image_path, x, y, width=img_width, height=img_height)

    snap_print(snap_images)
    # Save the PDF
    pdf_canvas.save()
    return export_filename


