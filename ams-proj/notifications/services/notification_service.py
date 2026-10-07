from notifications.tasks import (
    send_push_notification,
    send_email_notification,
    send_inapp_notification,
)
from notifications.models import (
    Notification,
    NotificationType,
)


class NotificationService:

    # ============================================================
    # CORE NOTIFICATION CREATION
    # ============================================================

    @staticmethod
    def _create(
        recipient,
        title,
        body,
        type,
        notiftype,
    ):
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            body=body,
            type=type,
        )

        if "push" in notiftype:
            send_push_notification.delay(
                notification.id
            )

        if "inapp" in notiftype:
            send_inapp_notification.delay(
                notification.id
            )
        print(f"NOTIFTYPE = {notiftype}", flush=True)
        if "email" in notiftype:
            print(f"QUEUING EMAIL TASK: notification_id={notification.id}", flush=True)
            send_email_notification.delay(
                notification.id
            )
            print("EMAIL TASK QUEUED", flush=True)

        return notification

    # ============================================================
    # ATTENDANCE
    # ============================================================

    @staticmethod
    def student_marked_absent(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Marked Absent",
            body=(
                f"You were marked absent for "
                f"{session.course_offering.course.name}"
            ),
            type=NotificationType.MARKED_ABSENT,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def student_marked_present(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Marked Present",
            body=(
                f"You were marked present for "
                f"{session.course_offering.course.name}"
            ),
            type=NotificationType.MARKED_PRESENT,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def student_marked_pending(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Attendance Pending",
            body=(
                f"Your attendance is pending for "
                f"{session.course_offering.course.name}"
            ),
            type=NotificationType.MARKED_PENDING,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def attendance_justified(student, session):
        NotificationService._create(
            recipient=student.user,
            title="Attendance Justified",
            body=(
                f"Your absence has been justified for "
                f"{session.course_offering.course.name}"
            ),
            type=NotificationType.ATTENDANCE_JUSTIFIED,
            notiftype=["push", "inapp"],
        )

    # ============================================================
    # AUTH
    # ============================================================

    @staticmethod
    def registered_successfully(user):
        NotificationService._create(
            recipient=user,
            title="Account Created",
            body=(
                f"Dear {user.get_full_name()}, "
                f"your account has been successfully created."
            ),
            type=NotificationType.REGISTERED,
            notiftype=["email", "inapp"],
        )

    @staticmethod
    def password_reset(user):
        NotificationService._create(
            recipient=user,
            title="Password Reset",
            body=(
                f"Dear {user.get_full_name()}, "
                f"your password has been reset successfully."
            ),
            type=NotificationType.PASSWORD_RESET,
            notiftype=["email", "inapp"],
        )

    @staticmethod
    def password_changed(user):
        NotificationService._create(
            recipient=user,
            title="Password Changed",
            body=(
                f"Dear {user.get_full_name()}, "
                f"your password has been changed successfully."
            ),
            type=NotificationType.PASSWORD_CHANGED,
            notiftype=["email", "inapp"],
        )

    # ============================================================
    # ACCOUNT
    # ============================================================

    @staticmethod
    def account_credentials(
        user,
        temporary_password,
    ):
        """
        Send newly-created account credentials.

        Accepts a CustomUser, Lecturer, or Student instance.
        The notification intentionally uses email only because
        the temporary password is sensitive information.
        """

        # Resolve the actual CustomUser
        if hasattr(user, "user"):
            account = user.user
        else:
            account = user

        NotificationService._create(
            recipient=account,
            title="Your Account Has Been Created",
            body=(
                f"Dear {account.get_full_name()},\n\n"
                f"Your SAMS account has been created successfully.\n\n"
                f"Login email: {account.school_email}\n"
                f"Temporary password: {temporary_password}\n\n"
                f"Please log in using these credentials and "
                f"change your password immediately.\n\n"
                f"For security reasons, do not share your "
                f"temporary password with anyone.\n\n"
                f"Regards,\n"
                f"SAMS Administration"
            ),
            type=NotificationType.REGISTERED,
            notiftype=["email"],
        )

    @staticmethod
    def password_reset_otp(
        user,
        otp,
    ):
        """
        Send password-reset OTP.

        OTP is sensitive, therefore email only.
        """

        NotificationService._create(
            recipient=user,
            title="Password Reset OTP",
            body=(
                f"Dear {user.get_full_name()},\n\n"
                f"Your OTP for password reset is: {otp}\n\n"
                f"This OTP expires in 10 minutes.\n"
                f"Do not share it with anyone.\n\n"
                f"Regards,\n"
                f"SAMS Administration"
            ),
            type=NotificationType.PASSWORD_RESET,
            notiftype=["email"],
        )

    # ============================================================
    # COURSE
    # ============================================================

    @staticmethod
    def course_created(user, course):
        NotificationService._create(
            recipient=user,
            title="Course Created",
            body=(
                f"The course {course.name} has been "
                f"successfully created."
            ),
            type=NotificationType.COURSE_CREATED,
            notiftype=["inapp"],
        )

    @staticmethod
    def course_updated(user, course):
        NotificationService._create(
            recipient=user,
            title="Course Updated",
            body=(
                f"The course {course.name} has been "
                f"successfully updated."
            ),
            type=NotificationType.COURSE_UPDATED,
            notiftype=["inapp"],
        )

    @staticmethod
    def course_deleted(user, course_name):
        NotificationService._create(
            recipient=user,
            title="Course Deleted",
            body=(
                f"The course {course_name} has been deleted."
            ),
            type=NotificationType.COURSE_DELETED,
            notiftype=["inapp"],
        )

    # ============================================================
    # COURSE OFFERING
    # ============================================================

    @staticmethod
    def course_offering_created(
        user,
        course_offering,
    ):
        NotificationService._create(
            recipient=user,
            title="Course Offering Created",
            body=(
                f"A new offering for "
                f"{course_offering.course.name} has been "
                f"created for "
                f"{course_offering.semester} "
                f"{course_offering.year}."
            ),
            type=NotificationType.COURSE_OFFERING_CREATED,
            notiftype=["inapp"],
        )

    @staticmethod
    def course_offering_updated(
        user,
        course_offering,
    ):
        NotificationService._create(
            recipient=user,
            title="Course Offering Updated",
            body=(
                f"The offering for "
                f"{course_offering.course.name} "
                f"({course_offering.semester} "
                f"{course_offering.year}) has been updated."
            ),
            type=NotificationType.COURSE_OFFERING_UPDATED,
            notiftype=["inapp"],
        )

    @staticmethod
    def course_offering_deleted(
        user,
        course_name,
    ):
        NotificationService._create(
            recipient=user,
            title="Course Offering Deleted",
            body=(
                f"The offering for {course_name} "
                f"has been deleted."
            ),
            type=NotificationType.COURSE_OFFERING_DELETED,
            notiftype=["inapp"],
        )

    # ============================================================
    # COURSE ASSIGNMENT
    # ============================================================

    @staticmethod
    def course_assignment_created(
        lecturer,
        course_offering,
    ):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment",
            body=(
                f"You have been assigned to teach "
                f"{course_offering.course.name} for "
                f"{course_offering.semester} "
                f"{course_offering.year}."
            ),
            type=NotificationType.ASSIGNMENT_CREATED,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def course_assignment_updated(
        lecturer,
        course_offering,
    ):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment Updated",
            body=(
                f"Your assignment for "
                f"{course_offering.course.name} "
                f"({course_offering.semester} "
                f"{course_offering.year}) has been updated."
            ),
            type=NotificationType.ASSIGNMENT_UPDATED,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def course_assignment_deleted(
        lecturer,
        course_name,
    ):
        NotificationService._create(
            recipient=lecturer.user,
            title="Course Assignment Removed",
            body=(
                f"You have been removed from teaching "
                f"{course_name}."
            ),
            type=NotificationType.ASSIGNMENT_DELETED,
            notiftype=["push", "inapp"],
        )

    # ============================================================
    # COURSE ENROLLMENT
    # ============================================================

    @staticmethod
    def course_enrollment_created(
        student,
        course_offering,
    ):
        NotificationService._create(
            recipient=student.user,
            title="Enrolled in Course",
            body=(
                f"You have been successfully enrolled in "
                f"{course_offering.course.name} for "
                f"{course_offering.semester} "
                f"{course_offering.year}."
            ),
            type=NotificationType.ENROLLMENT_CREATED,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def course_enrollment_updated(
        student,
        course_offering,
    ):
        NotificationService._create(
            recipient=student.user,
            title="Enrollment Updated",
            body=(
                f"Your enrollment in "
                f"{course_offering.course.name} "
                f"({course_offering.semester} "
                f"{course_offering.year}) has been updated."
            ),
            type=NotificationType.ENROLLMENT_UPDATED,
            notiftype=["push", "inapp"],
        )

    @staticmethod
    def course_enrollment_deleted(
        student,
        course_name,
    ):
        NotificationService._create(
            recipient=student.user,
            title="Enrollment Removed",
            body=(
                f"You have been removed from "
                f"{course_name}."
            ),
            type=NotificationType.ENROLLMENT_DELETED,
            notiftype=["push", "inapp"],
        )

    # ============================================================
    # SESSIONS
    # ============================================================

    @staticmethod
    def session_started(
        course_offering,
        students,
    ):
        for student in students:
            NotificationService._create(
                recipient=student.user,
                title="Session Started",
                body=(
                    f"A session for "
                    f"{course_offering.course.name} "
                    f"has just started."
                ),
                type=NotificationType.SESSION_STARTED,
                notiftype=["push", "inapp"],
            )

    @staticmethod
    def session_ended(
        course_offering,
        students,
    ):
        for student in students:
            NotificationService._create(
                recipient=student.user,
                title="Session Ended",
                body=(
                    f"The session for "
                    f"{course_offering.course.name} "
                    f"has ended."
                ),
                type=NotificationType.SESSION_ENDED,
                notiftype=["push", "inapp"],
            )