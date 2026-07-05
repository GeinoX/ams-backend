from tasks import send_push_notification, send_email_notification, send_inapp_notification
from models import Notification, NotificationType


class NotificationService:

    @staticmethod
    def _create(recipient, title, body, type, notiftype):

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            body=body,
            type=type
        )

        if "push" in notiftype:
            send_push_notification.delay(notification.id)

        if "inapp" in notiftype:
            send_inapp_notification.delay(notification.id)

        if "email" in notiftype:
            send_email_notification.delay(notification.id)

        return notification


    # ------- Attendance -------
    @staticmethod
    def student_marked_absent(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Marked Absent",
            body=f"You were marked absent for {session.course_offering.course.name}",
            type=NotificationType.MARKED_ABSENT,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def student_marked_present(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Marked Present",
            body=f"You were marked present for {session.course_offering.course.name}",
            type=NotificationType.MARKED_PRESENT,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def student_marked_pending(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Attendance Pending",
            body=f"Your attendance is pending for {session.course_offering.course.name}",
            type=NotificationType.MARKED_PENDING,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def attendance_justified(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Attendance Justified",
            body=f"Your absence has been justified for {session.course_offering.course.name}",
            type=NotificationType.ATTENDANCE_JUSTIFIED,
            notiftype=["push", "inapp"]
        )

    # ------- Auth -------
    @staticmethod
    def registered_successfully(user):
        NotificationService._create(
            recipient=user,
            title="Account Created",
            body=f"Dear {user.get_full_name()}, your account has been successfully created.",
            type=NotificationType.REGISTERED,
            notiftype=["email", "inapp"]
        )

    @staticmethod
    def password_reset(user):
        NotificationService._create(
            recipient=user,
            title="Password Reset",
            body=f"Dear {user.get_full_name()}, your password has been reset successfully.",
            type=NotificationType.PASSWORD_RESET,
            notiftype=["email", "inapp"]
        )

    @staticmethod
    def password_changed(user):
        NotificationService._create(
            recipient=user,
            title="Password Changed",
            body=f"Dear {user.get_full_name()}, your password has been changed successfully.",
            type=NotificationType.PASSWORD_CHANGED,
            notiftype=["email", "inapp"]
        )

    # ------- Account -------
    @staticmethod
    def account_credentials(user, temporary_password):
        NotificationService._create(
                recipient=user,
            title="Your Account Has Been Created",
            body=f"Dear {user.get_full_name()}, your account has been created. "
                 f"Your temporary password is: {temporary_password}. "
                 f"Please log in and change your password immediately.",
            type=NotificationType.REGISTERED,
            notiftype=["email"]  # ← email only, sensitive info
        )

    @staticmethod
    def password_reset_otp(user, otp):
     NotificationService._create(
            recipient=user,
            title="Password Reset OTP",
            body=f"Dear {user.get_full_name()}, your OTP for password reset is {otp}. "
                 f"It expires in 10 minutes. Do not share it with anyone.",
           type=NotificationType.PASSWORD_RESET,
           notiftype=["email"]  # ← email only, sensitive info
     )

    # ------- Course -------
    @staticmethod
    def course_created(user, course):
        NotificationService._create(
            recipient=user,
            title="Course Created",
            body=f"The course {course.name} has been successfully created.",
            type=NotificationType.COURSE_CREATED,
            notiftype=["inapp"]
        )

    @staticmethod
    def course_updated(user, course):
        NotificationService._create(
            recipient=user,
            title="Course Updated",
            body=f"The course {course.name} has been successfully updated.",
            type=NotificationType.COURSE_UPDATED,
            notiftype=["inapp"]
        )

    @staticmethod
    def course_deleted(user, course_name):
        NotificationService._create(
            recipient=user,
            title="Course Deleted",
            body=f"The course {course_name} has been deleted.",
            type=NotificationType.COURSE_DELETED,
            notiftype=["inapp"]
        )

    # ------- Course Offering -------
    @staticmethod
    def course_offering_created(user, course_offering):
        NotificationService._create(
            recipient=user,
            title="Course Offering Created",
            body=f"A new offering for {course_offering.course.name} has been created for {course_offering.semester} {course_offering.year}.",
            type=NotificationType.COURSE_OFFERING_CREATED,
            notiftype=["inapp"]
        )

    @staticmethod
    def course_offering_updated(user, course_offering):
        NotificationService._create(
            recipient=user,
            title="Course Offering Updated",
            body=f"The offering for {course_offering.course.name} ({course_offering.semester} {course_offering.year}) has been updated.",
            type=NotificationType.COURSE_OFFERING_UPDATED,
            notiftype=["inapp"]
        )

    @staticmethod
    def course_offering_deleted(user, course_name):
        NotificationService._create(
            recipient=user,
            title="Course Offering Deleted",
            body=f"The offering for {course_name} has been deleted.",
            type=NotificationType.COURSE_OFFERING_DELETED,
            notiftype=["inapp"]
        )

    # ------- Course Assignment -------
    @staticmethod
    def course_assignment_created(lecturer, course_offering):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment",
            body=f"You have been assigned to teach {course_offering.course.name} for {course_offering.semester} {course_offering.year}.",
            type=NotificationType.ASSIGNMENT_CREATED,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def course_assignment_updated(lecturer, course_offering):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment Updated",
            body=f"Your assignment for {course_offering.course.name} ({course_offering.semester} {course_offering.year}) has been updated.",
            type=NotificationType.ASSIGNMENT_UPDATED,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def course_assignment_deleted(lecturer, course_name):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment Removed",
            body=f"You have been removed from teaching {course_name}.",
            type=NotificationType.ASSIGNMENT_DELETED,
            notiftype=["push", "inapp"]
        )

    # ------- Course Enrollment -------
    @staticmethod
    def course_enrollment_created(student, course_offering):
        NotificationService._create(
            recipient=student.user,
            title="Enrolled in Course",
            body=f"You have been successfully enrolled in {course_offering.course.name} for {course_offering.semester} {course_offering.year}.",
            type=NotificationType.ENROLLMENT_CREATED,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def course_enrollment_updated(student, course_offering):
        NotificationService._create(
            recipient=student.user,
            title="Enrollment Updated",
            body=f"Your enrollment in {course_offering.course.name} ({course_offering.semester} {course_offering.year}) has been updated.",
            type=NotificationType.ENROLLMENT_UPDATED,
            notiftype=["push", "inapp"]
        )

    @staticmethod
    def course_enrollment_deleted(student, course_name):
        NotificationService._create(
            recipient=student.user,
            title="Enrollment Removed",
            body=f"You have been removed from {course_name}.",
            type=NotificationType.ENROLLMENT_DELETED,
            notiftype=["push", "inapp"]
        )

    # ------- Sessions -------
    @staticmethod
    def session_started(course_offering, students):
        for student in students:
            NotificationService._create(
                recipient=student.user,
                title="Session Started",
                body=f"A session for {course_offering.course.name} has just started.",
                type=NotificationType.SESSION_STARTED,
                notiftype=["push", "inapp"]
            )

    @staticmethod
    def session_ended(course_offering, students):
        for student in students:
            NotificationService._create(
                recipient=student.user,
                title="Session Ended",
                body=f"The session for {course_offering.course.name} has ended.",
                type=NotificationType.SESSION_ENDED,
                notiftype=["push", "inapp"]
            )