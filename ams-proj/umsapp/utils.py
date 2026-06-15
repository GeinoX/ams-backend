# umsapp/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_teacher_pending_attendance(pending_instance):
    """
    Pushes a pending attendance record to the teacher's WebSocket group
    so their device receives it in real-time without polling.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    session_id = str(pending_instance.session.session_id)
    teacher = pending_instance.session.course_offering.course_assignments.select_related(
        "lecturer"
    ).first()

    if not teacher:
        return

    teacher_id = str(teacher.lecturer.employee_id)
    group_name = f"session_{session_id}_teacher_{teacher_id}"

    added_student = pending_instance.added_student
    image = added_student.user.profile_image
    image_url = image.url if image else None

    payload = {
        "type": "send_pending_student",
        "data": {
            "pending_id": pending_instance.id,
            "session_id": session_id,
            "adder_name": pending_instance.adder.user.name,
            "adder_matricule": pending_instance.adder.matricule,
            "added_student_name": added_student.user.name,
            "added_student_matricule": added_student.matricule,
            "added_student_image": image_url,
            "timestamp": pending_instance.timestamp.isoformat(),
        },
    }

    async_to_sync(channel_layer.group_send)(group_name, payload)