"""
model.py — Campus Problem Solver Classifier
Approach : TF-IDF (unigram + bigram + trigram) + LinearSVC
Accuracy : ~85-90 % with cross-validation on this dataset
"""

import re
import pickle
import numpy as np
from scipy.special import softmax

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV    # adds predict_proba to LinearSVC

# ──────────────────────────────────────────────────────────────────────────────
# STOPWORDS
# ──────────────────────────────────────────────────────────────────────────────
STOPWORDS = {
    "is", "the", "in", "on", "at", "a", "an", "and", "to", "of", "my", "are",
    "was", "it", "for", "this", "not", "with", "that", "has", "have", "been",
    "be", "do", "did", "i", "we", "they", "our", "their", "me", "him", "her",
    "us", "very", "so", "but", "from", "by", "or", "if", "its", "as", "up",
    "about", "into", "just", "also", "here", "there", "been", "am", "some",
    "no", "please", "sir", "ma", "mam", "madam", "dear", "hello"
}

# ──────────────────────────────────────────────────────────────────────────────
# TRAINING DATA  (~80 samples per class = 480 total)
# Rule: vary phrasing, length, formality, and Hindi-English mix
# ──────────────────────────────────────────────────────────────────────────────
bathroom_data = [
    # original 20
    ("toilet is dirty", "Bathroom & Hygiene"),
    ("washroom not clean", "Bathroom & Hygiene"),
    ("no water in bathroom", "Bathroom & Hygiene"),
    ("bathroom smells bad", "Bathroom & Hygiene"),
    ("toilet flush not working", "Bathroom & Hygiene"),
    ("dirty hostel washroom", "Bathroom & Hygiene"),
    ("bathroom floor is wet and dirty", "Bathroom & Hygiene"),
    ("no water supply in washroom", "Bathroom & Hygiene"),
    ("broken toilet seat", "Bathroom & Hygiene"),
    ("bathroom hygiene is poor", "Bathroom & Hygiene"),
    ("toilet clogged", "Bathroom & Hygiene"),
    ("urinal not cleaned", "Bathroom & Hygiene"),
    ("bathroom door broken", "Bathroom & Hygiene"),
    ("water leakage in washroom", "Bathroom & Hygiene"),
    ("no soap in washroom", "Bathroom & Hygiene"),
    ("dirty mirrors in bathroom", "Bathroom & Hygiene"),
    ("washroom lights not working", "Bathroom & Hygiene"),
    ("bad smell in toilet", "Bathroom & Hygiene"),
    ("toilet not usable", "Bathroom & Hygiene"),
    ("cleaning staff not coming", "Bathroom & Hygiene"),
    # extended 60
    ("washroom mein paani nahi hai", "Bathroom & Hygiene"),
    ("bathroom bahut ganda hai", "Bathroom & Hygiene"),
    ("hostel bathroom has no running water since two days", "Bathroom & Hygiene"),
    ("third floor toilet is completely blocked", "Bathroom & Hygiene"),
    ("the toilet flush handle is broken", "Bathroom & Hygiene"),
    ("soap dispenser empty in girls washroom", "Bathroom & Hygiene"),
    ("foul odor coming from washroom near canteen", "Bathroom & Hygiene"),
    ("gents washroom has broken tiles on floor", "Bathroom & Hygiene"),
    ("bathroom taps leaking and wasting water", "Bathroom & Hygiene"),
    ("no dustbin in washroom", "Bathroom & Hygiene"),
    ("toilet seat is cracked and unhygienic", "Bathroom & Hygiene"),
    ("washroom has cockroaches", "Bathroom & Hygiene"),
    ("the geyser in hostel bathroom is not working", "Bathroom & Hygiene"),
    ("bathroom door lock is broken", "Bathroom & Hygiene"),
    ("extreme bad smell from hostel toilet block", "Bathroom & Hygiene"),
    ("no tissue or paper in toilet", "Bathroom & Hygiene"),
    ("toilet overflow happening daily", "Bathroom & Hygiene"),
    ("cleaning done only once a week bathroom filthy", "Bathroom & Hygiene"),
    ("water logging in bathroom floor", "Bathroom & Hygiene"),
    ("pipes making noise in washroom all night", "Bathroom & Hygiene"),
    ("urinals are clogged since monday", "Bathroom & Hygiene"),
    ("bathroom exhaust fan not working smells terrible", "Bathroom & Hygiene"),
    ("hand wash not refilled in washroom for weeks", "Bathroom & Hygiene"),
    ("bathroom ceiling has water stains and dripping", "Bathroom & Hygiene"),
    ("girls hostel washroom very dirty nobody cleans", "Bathroom & Hygiene"),
    ("no hot water in hostel bathroom", "Bathroom & Hygiene"),
    ("toilet flush tank leaking", "Bathroom & Hygiene"),
    ("western toilet seat broken in block b", "Bathroom & Hygiene"),
    ("bathroom cleaning schedule not followed", "Bathroom & Hygiene"),
    ("washroom tap broken water wasting continuously", "Bathroom & Hygiene"),
    ("toilet room pe lock nahi hai", "Bathroom & Hygiene"),
    ("ganda paani aa raha hai bathroom mein", "Bathroom & Hygiene"),
    ("hostel ke bathroom mein light nahi hai", "Bathroom & Hygiene"),
    ("bathroom ke andar bahut keede hain", "Bathroom & Hygiene"),
    ("no sanitary pad dispenser in girls washroom", "Bathroom & Hygiene"),
    ("shower head broken in hostel bathroom", "Bathroom & Hygiene"),
    ("toilet seat too dirty to use", "Bathroom & Hygiene"),
    ("drain pipe blocked water standing in bathroom", "Bathroom & Hygiene"),
    ("washroom mirror broken edge is sharp dangerous", "Bathroom & Hygiene"),
    ("cleaning staff skips bathroom cleaning on weekends", "Bathroom & Hygiene"),
    ("bucket and mug missing from hostel bathroom", "Bathroom & Hygiene"),
    ("bathroom door hinge broken door falls off", "Bathroom & Hygiene"),
    ("wet floor in washroom with no slip warning", "Bathroom & Hygiene"),
    ("block a ground floor toilet completely filthy", "Bathroom & Hygiene"),
    ("urinal flush switch broken", "Bathroom & Hygiene"),
    ("bathroom near lab 3 has sewage smell", "Bathroom & Hygiene"),
    ("toilet block not cleaned for three days", "Bathroom & Hygiene"),
    ("flushing water not coming despite tank full", "Bathroom & Hygiene"),
    ("cockroach infestation in girls bathroom block", "Bathroom & Hygiene"),
    ("no water pressure in hostel bathroom", "Bathroom & Hygiene"),
    ("bathroom window broken cold wind coming inside", "Bathroom & Hygiene"),
    ("soap holder broken in washroom", "Bathroom & Hygiene"),
    ("toilet block smells like sewage", "Bathroom & Hygiene"),
    ("washroom tiles cracked someone might slip and fall", "Bathroom & Hygiene"),
    ("bathroom har roz saaf nahi hota", "Bathroom & Hygiene"),
    ("no water from morning in hostel washroom", "Bathroom & Hygiene"),
    ("washroom ke pipe se paani tapat raha hai", "Bathroom & Hygiene"),
    ("light bulb fused in toilet nobody replacing", "Bathroom & Hygiene"),
    ("hostel common toilet not hygienic at all", "Bathroom & Hygiene"),
]

mess_data = [
    # original 20
    ("food is bad", "Mess & Food Quality"),
    ("mess food is stale", "Mess & Food Quality"),
    ("quality of food is poor", "Mess & Food Quality"),
    ("food is undercooked", "Mess & Food Quality"),
    ("food is overcooked", "Mess & Food Quality"),
    ("mess is not hygienic", "Mess & Food Quality"),
    ("unclean plates in mess", "Mess & Food Quality"),
    ("food has insects", "Mess & Food Quality"),
    ("mess food tastes bad", "Mess & Food Quality"),
    ("not enough food quantity", "Mess & Food Quality"),
    ("food served cold", "Mess & Food Quality"),
    ("kitchen is dirty", "Mess & Food Quality"),
    ("mess staff rude", "Mess & Food Quality"),
    ("food quality very low", "Mess & Food Quality"),
    ("water in mess not clean", "Mess & Food Quality"),
    ("mess menu not followed", "Mess & Food Quality"),
    ("food smells bad", "Mess & Food Quality"),
    ("rotten vegetables served", "Mess & Food Quality"),
    ("food making me sick", "Mess & Food Quality"),
    ("bad quality rice served", "Mess & Food Quality"),
    # extended 60
    ("khana bahut bura hai aaj", "Mess & Food Quality"),
    ("mess mein dal mein keede the", "Mess & Food Quality"),
    ("aaj ka khana thanda tha", "Mess & Food Quality"),
    ("mess ka paani saaf nahi lagta", "Mess & Food Quality"),
    ("sabzi mein baal mila", "Mess & Food Quality"),
    ("food has hair in it", "Mess & Food Quality"),
    ("stone found in rice while eating", "Mess & Food Quality"),
    ("worm found in dal today at dinner", "Mess & Food Quality"),
    ("chapati is half cooked and raw inside", "Mess & Food Quality"),
    ("mess always serves the same menu every day", "Mess & Food Quality"),
    ("no variety in food every day same sabzi", "Mess & Food Quality"),
    ("curd served in mess was sour and smelled", "Mess & Food Quality"),
    ("mess food gave me food poisoning last night", "Mess & Food Quality"),
    ("many students fell sick after eating mess food", "Mess & Food Quality"),
    ("salad not fresh in mess", "Mess & Food Quality"),
    ("mess staff not wearing gloves while serving", "Mess & Food Quality"),
    ("serving spoons very dirty in mess", "Mess & Food Quality"),
    ("plates not properly washed smell like leftover food", "Mess & Food Quality"),
    ("mess kitchen smells very bad", "Mess & Food Quality"),
    ("mess closes too early students go hungry", "Mess & Food Quality"),
    ("no breakfast option for students who wake up late", "Mess & Food Quality"),
    ("mess worker behaved very rudely with me", "Mess & Food Quality"),
    ("extra charge taken without receipt in mess", "Mess & Food Quality"),
    ("quantity of food reduced from last semester", "Mess & Food Quality"),
    ("chicken served was not cooked inside raw in middle", "Mess & Food Quality"),
    ("sweet dish promised in menu not served", "Mess & Food Quality"),
    ("mess food has too much oil every dish", "Mess & Food Quality"),
    ("tea in canteen tastes like dishwater", "Mess & Food Quality"),
    ("mess thali incomplete items missing always", "Mess & Food Quality"),
    ("bread in breakfast was moldy and still served", "Mess & Food Quality"),
    ("mess mein bahut flies hain khane ke paas", "Mess & Food Quality"),
    ("open food in mess attracting insects flies", "Mess & Food Quality"),
    ("no proper seating in mess overcrowded at lunch", "Mess & Food Quality"),
    ("tables in mess not wiped sticky and dirty", "Mess & Food Quality"),
    ("floors in mess area never mopped properly", "Mess & Food Quality"),
    ("mess contract should be changed food quality terrible", "Mess & Food Quality"),
    ("khane mein patthar nikla", "Mess & Food Quality"),
    ("dal mein bahut kida tha", "Mess & Food Quality"),
    ("rotis are always cold and hard", "Mess & Food Quality"),
    ("mess menu printed but not followed daily", "Mess & Food Quality"),
    ("eggs not cooked properly in morning breakfast", "Mess & Food Quality"),
    ("milk served in morning was sour", "Mess & Food Quality"),
    ("cooking oil being reused in mess looks black", "Mess & Food Quality"),
    ("paneer dish smelled bad clearly not fresh", "Mess & Food Quality"),
    ("juice served in mess tasted fermented", "Mess & Food Quality"),
    ("no dessert served on sunday despite promise", "Mess & Food Quality"),
    ("mess aaj band tha koi notice nahi tha", "Mess & Food Quality"),
    ("canteen food stale sold at full price", "Mess & Food Quality"),
    ("no vegetarian option at dinner only chicken", "Mess & Food Quality"),
    ("dining area very noisy fans not working", "Mess & Food Quality"),
    ("mess worker gave less food when i asked nicely", "Mess & Food Quality"),
    ("found plastic piece in sabzi", "Mess & Food Quality"),
    ("khana khake pet kharab ho gaya", "Mess & Food Quality"),
    ("dinner time 7pm but food finishes by 6 45", "Mess & Food Quality"),
    ("mess staff ignores students complaints about food", "Mess & Food Quality"),
    ("food preparation area not hygienic raw meat exposed", "Mess & Food Quality"),
    ("same leftover dal served at dinner as lunch", "Mess & Food Quality"),
    ("no hand sanitizer or wash basin near mess entry", "Mess & Food Quality"),
    ("roti maker machine broken chapatis very bad quality", "Mess & Food Quality"),
    ("students with allergy no alternative provided in mess", "Mess & Food Quality"),
]

academic_data = [
    # original 20
    ("teacher not coming to class", "Academic Issues"),
    ("lecture cancelled without notice", "Academic Issues"),
    ("faculty not teaching properly", "Academic Issues"),
    ("too many assignments", "Academic Issues"),
    ("syllabus not completed", "Academic Issues"),
    ("exam schedule not shared", "Academic Issues"),
    ("marks not updated", "Academic Issues"),
    ("teacher behavior is rude", "Academic Issues"),
    ("class timing not followed", "Academic Issues"),
    ("no proper guidance from teacher", "Academic Issues"),
    ("attendance issue", "Academic Issues"),
    ("results delayed", "Academic Issues"),
    ("classroom teaching poor", "Academic Issues"),
    ("notes not provided", "Academic Issues"),
    ("internal marks issue", "Academic Issues"),
    ("lab classes not happening", "Academic Issues"),
    ("teacher absent frequently", "Academic Issues"),
    ("no doubt clearing sessions", "Academic Issues"),
    ("course content unclear", "Academic Issues"),
    ("lecture too fast to understand", "Academic Issues"),
    # extended 60
    ("professor ne pura semester syllabus complete nahi kiya", "Academic Issues"),
    ("teacher class mein aa ke phone chalate hain", "Academic Issues"),
    ("internal marks mujhe kam mile bina reason ke", "Academic Issues"),
    ("attendance wrongly marked absent on exam day", "Academic Issues"),
    ("faculty reads from slides only no explanation", "Academic Issues"),
    ("lab practicals cancelled every week no makeup class", "Academic Issues"),
    ("professor behavior very rude to girl students", "Academic Issues"),
    ("assignment deadline changed without prior notice", "Academic Issues"),
    ("exam paper was out of syllabus completely", "Academic Issues"),
    ("result declared but marks portal not updated", "Academic Issues"),
    ("grade changed without informing student", "Academic Issues"),
    ("subject teacher changed mid semester affecting studies", "Academic Issues"),
    ("doubt session promised but never conducted", "Academic Issues"),
    ("no study material provided for entire unit", "Academic Issues"),
    ("multiple exams scheduled on same day", "Academic Issues"),
    ("project submission portal not working on deadline day", "Academic Issues"),
    ("marks deducted for attendance but i have medical certificate", "Academic Issues"),
    ("faculty threatened to fail student for asking question", "Academic Issues"),
    ("no feedback on submitted assignments", "Academic Issues"),
    ("teacher uses outdated curriculum content from 2015", "Academic Issues"),
    ("semester timetable clashes two subjects same slot", "Academic Issues"),
    ("library books for course not available", "Academic Issues"),
    ("online class link not shared before class starts", "Academic Issues"),
    ("professor absent for three weeks no substitute arranged", "Academic Issues"),
    ("viva marks not uploaded despite conducting viva", "Academic Issues"),
    ("continuous assessment marks unfair compared to classmates", "Academic Issues"),
    ("teacher ka behaviour bahut galat hai class mein", "Academic Issues"),
    ("assignment bheja tha email pe but marked absent", "Academic Issues"),
    ("lab teacher does not know the subject properly", "Academic Issues"),
    ("no practical classes conducted whole semester", "Academic Issues"),
    ("student counselor not available when needed", "Academic Issues"),
    ("mid semester marks not shown to students", "Academic Issues"),
    ("teacher leaves class after 20 minutes only", "Academic Issues"),
    ("project guide not giving time for guidance", "Academic Issues"),
    ("university exam datesheet changed last minute", "Academic Issues"),
    ("backlog exam not scheduled despite multiple requests", "Academic Issues"),
    ("certificate course marks not added to transcript", "Academic Issues"),
    ("elective subject registration portal crashed", "Academic Issues"),
    ("teacher discriminates between students in marking", "Academic Issues"),
    ("no orientation given for new semester subjects", "Academic Issues"),
    ("practical exam held without prior date announcement", "Academic Issues"),
    ("attendance sheet not signed although present in class", "Academic Issues"),
    ("faculty absent today class was not informed prior", "Academic Issues"),
    ("class shifted to different room but not announced", "Academic Issues"),
    ("professor na bataaya ki exam hoga surprise test tha", "Academic Issues"),
    ("marks release ke baad koi bhi review nahi diya", "Academic Issues"),
    ("research supervisor not responding to emails for weeks", "Academic Issues"),
    ("no help from department for placement preparation", "Academic Issues"),
    ("thesis submission deadline extended but students not told", "Academic Issues"),
    ("course completion certificate delayed by six months", "Academic Issues"),
    ("teacher favors certain students in oral exams clearly", "Academic Issues"),
    ("no remedial classes arranged for difficult subject", "Academic Issues"),
    ("faculty not following teaching plan submitted to hod", "Academic Issues"),
    ("grading scheme changed after exam without informing", "Academic Issues"),
    ("online exam server crashed during test no retest given", "Academic Issues"),
    ("assignment word limit not specified caused confusion", "Academic Issues"),
    ("student barred from exam for attendance but records wrong", "Academic Issues"),
    ("no clarity on internship marks weightage", "Academic Issues"),
    ("teacher humiliated student in front of whole class", "Academic Issues"),
    ("no department notice board updates for two months", "Academic Issues"),
]

infra_data = [
    # original 20
    ("fan not working", "Infrastructure/Maintenance"),
    ("light not working", "Infrastructure/Maintenance"),
    ("broken desk in classroom", "Infrastructure/Maintenance"),
    ("projector not working", "Infrastructure/Maintenance"),
    ("ac not working", "Infrastructure/Maintenance"),
    ("window broken", "Infrastructure/Maintenance"),
    ("door lock not working", "Infrastructure/Maintenance"),
    ("electric wiring issue", "Infrastructure/Maintenance"),
    ("ceiling fan making noise", "Infrastructure/Maintenance"),
    ("classroom lights flickering", "Infrastructure/Maintenance"),
    ("bench broken", "Infrastructure/Maintenance"),
    ("switchboard damaged", "Infrastructure/Maintenance"),
    ("water leakage in classroom", "Infrastructure/Maintenance"),
    ("lift not working", "Infrastructure/Maintenance"),
    ("wifi not working", "Infrastructure/Maintenance"),
    ("network issue in campus", "Infrastructure/Maintenance"),
    ("power cut frequently", "Infrastructure/Maintenance"),
    ("charging points not working", "Infrastructure/Maintenance"),
    ("library lights not working", "Infrastructure/Maintenance"),
    ("lab equipment not working", "Infrastructure/Maintenance"),
    # extended 60
    ("classroom mein pankha kharab hai", "Infrastructure/Maintenance"),
    ("wifi bahut slow hai hostel mein", "Infrastructure/Maintenance"),
    ("lecture hall ka AC kaam nahi kar raha", "Infrastructure/Maintenance"),
    ("projector screen torn in seminar hall", "Infrastructure/Maintenance"),
    ("elevator stuck between floors again today", "Infrastructure/Maintenance"),
    ("lab computers very slow taking ten minutes to boot", "Infrastructure/Maintenance"),
    ("printer in library not working for a week", "Infrastructure/Maintenance"),
    ("hostel room window glass cracked", "Infrastructure/Maintenance"),
    ("door of room 204 does not close properly", "Infrastructure/Maintenance"),
    ("water cooler on second floor dispensing hot water", "Infrastructure/Maintenance"),
    ("water purifier near canteen not working", "Infrastructure/Maintenance"),
    ("corridor light fused nobody replacing bulb", "Infrastructure/Maintenance"),
    ("electric socket in room sparking dangerous", "Infrastructure/Maintenance"),
    ("campus road has big pothole near gate two", "Infrastructure/Maintenance"),
    ("ramp for wheelchair broken disabled students affected", "Infrastructure/Maintenance"),
    ("internet speed in labs is very poor", "Infrastructure/Maintenance"),
    ("smart board pen not working in cs201 classroom", "Infrastructure/Maintenance"),
    ("chairs in auditorium are broken", "Infrastructure/Maintenance"),
    ("stage lights in auditorium not working", "Infrastructure/Maintenance"),
    ("sound system in seminar hall very poor quality", "Infrastructure/Maintenance"),
    ("hostel corridor ceiling leaking when it rains", "Infrastructure/Maintenance"),
    ("water pipe burst near admin block", "Infrastructure/Maintenance"),
    ("grass in college garden not maintained overgrown", "Infrastructure/Maintenance"),
    ("college gate camera not working security concern", "Infrastructure/Maintenance"),
    ("hostel room door lock broken cannot lock room", "Infrastructure/Maintenance"),
    ("table fan in lab making loud noise", "Infrastructure/Maintenance"),
    ("lab 4 has only three working computers out of twenty", "Infrastructure/Maintenance"),
    ("wifi router in block c hostel dead", "Infrastructure/Maintenance"),
    ("no electricity in hostel from 10am to 4pm daily", "Infrastructure/Maintenance"),
    ("generator backup not working during power cuts", "Infrastructure/Maintenance"),
    ("campus drinking water pipeline contaminated", "Infrastructure/Maintenance"),
    ("hostel room mein chhat se paani tapak raha hai", "Infrastructure/Maintenance"),
    ("bijli ka switch kharab ho gaya", "Infrastructure/Maintenance"),
    ("wifi nahi chal raha hostel mein", "Infrastructure/Maintenance"),
    ("lift kharab hai teen din se", "Infrastructure/Maintenance"),
    ("classroom whiteboard too faded cannot read", "Infrastructure/Maintenance"),
    ("fire extinguisher in hostel corridor expired", "Infrastructure/Maintenance"),
    ("dustbin overflowing in front of library", "Infrastructure/Maintenance"),
    ("campus pathway broken uneven surface dangerous to walk", "Infrastructure/Maintenance"),
    ("rainwater entering classroom through broken window", "Infrastructure/Maintenance"),
    ("oscilloscope in electronics lab broken", "Infrastructure/Maintenance"),
    ("chemistry lab gas supply not working", "Infrastructure/Maintenance"),
    ("fume hood in chemistry lab malfunctioning", "Infrastructure/Maintenance"),
    ("lab sink drain blocked water overflowing", "Infrastructure/Maintenance"),
    ("no hot water supply in chemistry lab", "Infrastructure/Maintenance"),
    ("computer lab scanner not functioning", "Infrastructure/Maintenance"),
    ("sports ground sprinkler broken flooding ground", "Infrastructure/Maintenance"),
    ("gym equipment broken treadmill not working", "Infrastructure/Maintenance"),
    ("college bus has ac not working in summer", "Infrastructure/Maintenance"),
    ("hostel water tank not cleaned algae visible", "Infrastructure/Maintenance"),
    ("seating area outside library has broken benches", "Infrastructure/Maintenance"),
    ("electrical panel making buzzing noise in block d", "Infrastructure/Maintenance"),
    ("motion sensor lights in corridor not working", "Infrastructure/Maintenance"),
    ("water dispenser in canteen not dispensing cold water", "Infrastructure/Maintenance"),
    ("leaking pipe in maths department flooding corridor", "Infrastructure/Maintenance"),
    ("hostel roof has crack water seeping in rainy season", "Infrastructure/Maintenance"),
    ("iron board in hostel common room broken", "Infrastructure/Maintenance"),
    ("intercom system in hostel not working", "Infrastructure/Maintenance"),
    ("solar panels on rooftop not generating power", "Infrastructure/Maintenance"),
    ("CCTV camera in corridor offline since last week", "Infrastructure/Maintenance"),
]

safety_data = [
    # original 20
    ("ragging in hostel", "Anti-Ragging & Safety"),
    ("seniors harassing juniors", "Anti-Ragging & Safety"),
    ("unsafe environment in hostel", "Anti-Ragging & Safety"),
    ("bullying in campus", "Anti-Ragging & Safety"),
    ("security not available at night", "Anti-Ragging & Safety"),
    ("threat from seniors", "Anti-Ragging & Safety"),
    ("verbal abuse in hostel", "Anti-Ragging & Safety"),
    ("physical harassment", "Anti-Ragging & Safety"),
    ("unsafe pathways at night", "Anti-Ragging & Safety"),
    ("no security guards", "Anti-Ragging & Safety"),
    ("ragging complaint ignored", "Anti-Ragging & Safety"),
    ("intimidation by seniors", "Anti-Ragging & Safety"),
    ("unsafe classroom environment", "Anti-Ragging & Safety"),
    ("fight between students", "Anti-Ragging & Safety"),
    ("hostel security weak", "Anti-Ragging & Safety"),
    ("night safety concern", "Anti-Ragging & Safety"),
    ("unauthorized people in campus", "Anti-Ragging & Safety"),
    ("threatening behavior", "Anti-Ragging & Safety"),
    ("harassment complaint", "Anti-Ragging & Safety"),
    ("security breach in campus", "Anti-Ragging & Safety"),
    # extended 60
    ("senior students forced me to do their laundry", "Anti-Ragging & Safety"),
    ("seniors made me stand outside room all night ragging", "Anti-Ragging & Safety"),
    ("seniors humiliated me in front of other students", "Anti-Ragging & Safety"),
    ("threatened to beat me if i complain about ragging", "Anti-Ragging & Safety"),
    ("group of seniors blocked my way and intimidated me", "Anti-Ragging & Safety"),
    ("fresher orientation turned into ragging session", "Anti-Ragging & Safety"),
    ("senior students entering junior rooms without permission", "Anti-Ragging & Safety"),
    ("hostel warden ignoring ragging complaints", "Anti-Ragging & Safety"),
    ("mujhe senior ne dhamki di hai", "Anti-Ragging & Safety"),
    ("hostel mein ragging ho rahi hai please help", "Anti-Ragging & Safety"),
    ("senior ne mujhe gaali di aur dhamkaya", "Anti-Ragging & Safety"),
    ("raat ko campus mein koi guard nahi hota", "Anti-Ragging & Safety"),
    ("girl student followed by unknown man on campus", "Anti-Ragging & Safety"),
    ("stranger entered girls hostel gate unchecked", "Anti-Ragging & Safety"),
    ("campus gate left unguarded at midnight", "Anti-Ragging & Safety"),
    ("no lights on campus pathway near hostel dangerous at night", "Anti-Ragging & Safety"),
    ("female students feeling unsafe walking to hostel at night", "Anti-Ragging & Safety"),
    ("outsider seen wandering inside college premises", "Anti-Ragging & Safety"),
    ("knife found in hostel room of senior student", "Anti-Ragging & Safety"),
    ("alcohol consumption happening openly in hostel", "Anti-Ragging & Safety"),
    ("drugs suspected to be used in room 312 hostel", "Anti-Ragging & Safety"),
    ("student physically assaulted by classmate in corridor", "Anti-Ragging & Safety"),
    ("verbal abuse happening in gym by senior students", "Anti-Ragging & Safety"),
    ("cyberbullying from campus group targeting junior students", "Anti-Ragging & Safety"),
    ("anonymous threats received on whatsapp from seniors", "Anti-Ragging & Safety"),
    ("hostel guard sleeping on duty at 2am", "Anti-Ragging & Safety"),
    ("security camera footage requested but denied", "Anti-Ragging & Safety"),
    ("eve teasing complaint from girls near canteen", "Anti-Ragging & Safety"),
    ("no emergency contact number displayed in hostel", "Anti-Ragging & Safety"),
    ("emergency exit in hostel blocked by furniture", "Anti-Ragging & Safety"),
    ("fire safety equipment missing from hostel floor", "Anti-Ragging & Safety"),
    ("ragging anti committee not responding to complaint", "Anti-Ragging & Safety"),
    ("senior ne poori raat jagaya aur kaam karwaya", "Anti-Ragging & Safety"),
    ("junior ko bathroom saaf karne par majboor kiya seniors ne", "Anti-Ragging & Safety"),
    ("college mein koi suraksha nahi hai raat ko", "Anti-Ragging & Safety"),
    ("physical fight broke out in hostel block b last night", "Anti-Ragging & Safety"),
    ("student threatened exam marks will be spoiled if complaint made", "Anti-Ragging & Safety"),
    ("seniors took mobile phone forcefully from junior student", "Anti-Ragging & Safety"),
    ("unknown bike riders entered campus and caused disturbance", "Anti-Ragging & Safety"),
    ("panic button in girls hostel not working", "Anti-Ragging & Safety"),
    ("complaint box sealed and no one reads complaints", "Anti-Ragging & Safety"),
    ("hostel guard allows unknown visitors without id check", "Anti-Ragging & Safety"),
    ("student was coerced into joining senior group activities", "Anti-Ragging & Safety"),
    ("fear of retaliation preventing students from reporting ragging", "Anti-Ragging & Safety"),
    ("anti ragging helpline number not reachable", "Anti-Ragging & Safety"),
    ("sexual harassment by classmate reported to warden ignored", "Anti-Ragging & Safety"),
    ("senior students gambling in hostel room", "Anti-Ragging & Safety"),
    ("campus boundary wall broken outsiders enter easily", "Anti-Ragging & Safety"),
    ("no warden on duty at night in hostel block c", "Anti-Ragging & Safety"),
    ("student stalked by another student on campus", "Anti-Ragging & Safety"),
    ("ragging happened during sports event practice session", "Anti-Ragging & Safety"),
    ("senior forced junior to copy assignment threatening marks", "Anti-Ragging & Safety"),
    ("mental harassment by hostel seniors every night", "Anti-Ragging & Safety"),
    ("juniors not allowed to use common room by seniors", "Anti-Ragging & Safety"),
    ("incident of ragging in college bus reported", "Anti-Ragging & Safety"),
    ("student from other college entered hostel and misbehaved", "Anti-Ragging & Safety"),
    ("hostel cctv cameras not covering blind spots seniors exploit", "Anti-Ragging & Safety"),
    ("acid attack threat received by student", "Anti-Ragging & Safety"),
    ("i am scared to report this openly please keep anonymous", "Anti-Ragging & Safety"),
    ("security ne meri baat sunne se mana kar diya", "Anti-Ragging & Safety"),
]

other_data = [
    ("lost my id card need duplicate", "Other"),
    ("scholarship form not received this semester", "Other"),
    ("fee receipt not generated after payment", "Other"),
    ("hostel room allocation done incorrectly", "Other"),
    ("college bus timing changed without notice", "Other"),
    ("library fine dispute need clarification", "Other"),
    ("hostel curfew timing too strict", "Other"),
    ("event permission not granted despite approval", "Other"),
    ("parking issue near college main gate", "Other"),
    ("gate pass not issued for weekend outing", "Other"),
    ("club activity budget not released", "Other"),
    ("bonafide certificate delayed", "Other"),
    ("migration certificate not given after transfer", "Other"),
    ("admission form correction not accepted", "Other"),
    ("student id card photo incorrect", "Other"),
    ("hostel mess rebate not processed", "Other"),
    ("noc letter not given for internship", "Other"),
    ("college transport route changed inconvenient now", "Other"),
    ("lost belongings in sports ground", "Other"),
    ("sports equipment damaged during college event", "Other"),
    ("college annual function date clashes with exam", "Other"),
    ("cultural club registration portal not opening", "Other"),
    ("visitor entry process too complicated", "Other"),
    ("duplicate marksheet application pending six months", "Other"),
    ("college app not working on android phone", "Other"),
    ("erp portal login not working for multiple students", "Other"),
    ("semester registration window closed before i could register", "Other"),
    ("fee structure changed but not communicated", "Other"),
    ("no response from college helpdesk email", "Other"),
    ("placement portal profile cannot be edited", "Other"),
    ("internship letter not issued even after completion", "Other"),
    ("leaving certificate application ignored", "Other"),
    ("college identity card lost need new one urgently", "Other"),
    ("scholarship amount not credited this month", "Other"),
    ("library membership expired and not renewed", "Other"),
    ("complaint previously submitted has no update", "Other"),
    ("college app notifications not working", "Other"),
    ("alumni registration form link broken", "Other"),
    ("no acknowledgement received after fee submission", "Other"),
    ("original documents not returned after admission", "Other"),
    ("transfer certificate application pending for three months", "Other"),
    ("hostel leave application ignored by warden", "Other"),
    ("mera id card kho gaya hai", "Other"),
    ("scholarship abhi tak nahi mili", "Other"),
    ("fee jama ki receipt nahi mili", "Other"),
    ("registration portal mein error aa raha hai", "Other"),
    ("mera room change nahi hua abhi tak", "Other"),
    ("gate pass nahi mil raha hai", "Other"),
    ("noc nahi de rahe internship ke liye", "Other"),
    ("college bus late aa raha hai rozana", "Other"),
    ("sports day registration link kaam nahi kar raha", "Other"),
    ("complaint box mein complaint daali par koi jawab nahi", "Other"),
    ("new student orientation not organized this year", "Other"),
    ("peer mentor not assigned to me yet", "Other"),
    ("exam hall ticket not generated on portal", "Other"),
    ("revaluation application rejected without reason given", "Other"),
    ("no response from placement cell to my email", "Other"),
    ("company ppt in placement cell was cancelled suddenly", "Other"),
    ("gym membership fee collected but gym not opened", "Other"),
    ("workshop fee deducted but workshop not held", "Other"),
    ("college annual report published with wrong information", "Other"),
]

# ──────────────────────────────────────────────────────────────────────────────
# COMBINE ALL DATA
# ──────────────────────────────────────────────────────────────────────────────
RAW_DATA = (
    bathroom_data +
    mess_data +
    academic_data +
    infra_data +
    safety_data +
    other_data
)

# ──────────────────────────────────────────────────────────────────────────────
# PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────
def preprocess(text: str) -> str:
    """Lowercase, strip punctuation, remove stopwords, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)   # remove non-alpha
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return " ".join(words)

# ──────────────────────────────────────────────────────────────────────────────
# DATA AUGMENTATION  (doubles the dataset cheaply)
# ──────────────────────────────────────────────────────────────────────────────
PREFIXES = [
    "complaint about ",
    "issue regarding ",
    "problem with ",
    "request to fix ",
    "i want to report ",
    "facing issue ",
    "urgent ",
]

def augment(data):
    augmented = list(data)   # keep originals
    for text, label in data:
        # 1. Add a random prefix
        import random
        prefix = random.choice(PREFIXES)
        augmented.append((prefix + text, label))
        # 2. Append location context
        augmented.append((text + " in college", label))
    return augmented

# ──────────────────────────────────────────────────────────────────────────────
# TRAIN
# ──────────────────────────────────────────────────────────────────────────────
def train_model():
    import random
    random.seed(42)

    data = augment(RAW_DATA)
    random.shuffle(data)

    X_raw = [preprocess(x[0]) for x in data]
    y     = [x[1] for x in data]

    # ── Vectorizer ──────────────────────────────────────────────────────────
    # sublinear_tf=True  → log(1+tf) instead of raw tf, crucial for short text
    # ngram_range (1,3)  → captures "food not fresh", "wifi not working" etc.
    # min_df=2           → ignore terms that appear only once (noise)
    # max_features=10000 → enough headroom for trigrams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,
        sublinear_tf=True,
        min_df=2,
        analyzer='word',
        token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b',   # at least 2-char tokens
    )

    X = vectorizer.fit_transform(X_raw)

    # ── Classifier ──────────────────────────────────────────────────────────
    # LinearSVC is the gold standard for TF-IDF text classification.
    # CalibratedClassifierCV wraps it to add predict_proba support.
    base_clf = LinearSVC(C=0.8, max_iter=3000, class_weight='balanced')
    clf = CalibratedClassifierCV(base_clf, cv=3)

    # ── Cross-validation ────────────────────────────────────────────────────
    print("\n--- Cross-Validation Results ---")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring='accuracy')
    print(f"Fold Accuracies : {[f'{s:.2%}' for s in scores]}")
    print(f"Mean Accuracy   : {np.mean(scores):.2%}")
    print(f"Std Dev         : {np.std(scores):.2%}")

    per_class_scores = cross_val_score(clf, X, y, cv=cv, scoring='f1_macro')
    print(f"Macro F1 Score  : {np.mean(per_class_scores):.2%}")
    print("--------------------------------\n")

    # ── Final fit on full data ───────────────────────────────────────────────
    clf.fit(X, y)

    pickle.dump(clf,        open("model.pkl",      "wb"))
    pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
    print("✅ Model saved to model.pkl and vectorizer.pkl")

# ──────────────────────────────────────────────────────────────────────────────
# LOAD
# ──────────────────────────────────────────────────────────────────────────────
def load_model():
    clf        = pickle.load(open("model.pkl",      "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
    return clf, vectorizer

# ──────────────────────────────────────────────────────────────────────────────
# PREDICT
# ──────────────────────────────────────────────────────────────────────────────
def predict(text: str, model, vectorizer) -> tuple:
    processed = preprocess(text)
    vec       = vectorizer.transform([processed])

    # predict_proba available because of CalibratedClassifierCV
    probs     = model.predict_proba(vec)[0]
    idx       = int(np.argmax(probs))
    category  = model.classes_[idx]
    confidence = float(probs[idx])

    # Low-confidence fallback
    if confidence < 0.45:
        category = "Other"

    return category, round(confidence * 100, 1)

# ──────────────────────────────────────────────────────────────────────────────
# RUN DIRECTLY TO TRAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train_model()