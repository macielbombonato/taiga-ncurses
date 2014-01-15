from concurrent.futures import Future
from unittest import mock

from gmncurses.ui import signals, views
from gmncurses import controllers, config
from gmncurses.executor import Executor
from gmncurses.core import StateMachine

from tests import factories


def test_sprints_controller_show_the_help_popup():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)

    assert not hasattr(project_detail_controller.view.sprint, "help_popup")
    project_detail_controller.handle(config.ProjectMilestoneKeys.HELP)
    assert hasattr(project_detail_controller.view.sprint, "help_popup")

def test_sprints_controller_close_the_help_popup():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.HELP)

    assert hasattr(project_detail_controller.view.sprint, "help_popup")
    help_popup = project_detail_controller.view.sprint.help_popup
    signals.emit(help_popup.close_button, "click")
    assert not hasattr(project_detail_controller.view.sprint, "help_popup")

def test_sprints_controller_reload():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    executor.milestone.reset_mock()
    executor.milestone_stats.reset_mock()
    executor.user_stories.reset_mock()
    executor.tasks.reset_mock()

    assert executor.milestone.call_count == 0
    assert executor.milestone_stats.call_count == 0
    assert executor.user_stories.call_count == 0
    assert executor.tasks.call_count == 0
    project_detail_controller.handle(config.ProjectMilestoneKeys.RELOAD)
    assert executor.milestone.call_count == 1
    assert executor.milestone_stats.call_count == 1
    assert executor.user_stories.call_count == 1
    assert executor.tasks.call_count == 1

def test_sprint_controller_show_the_edit_user_story_form():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)

    assert not hasattr(project_detail_controller.sprint.view, "user_story_form")
    project_detail_controller.handle(config.ProjectMilestoneKeys.EDIT_USER_STORY_OR_TASK)
    assert hasattr(project_detail_controller.sprint.view, "user_story_form")
    assert (project_detail_controller.sprint.view.user_story_form.user_story ==
            project_detail_controller.sprint.view.taskboard.widget.get_focus().user_story)

def test_sprint_controller_cancel_the_edit_user_story_form():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.EDIT_USER_STORY_OR_TASK)

    assert hasattr(project_detail_controller.sprint.view, "user_story_form")
    form = project_detail_controller.sprint.view.user_story_form
    signals.emit(form.cancel_button, "click")
    assert not hasattr(project_detail_controller.sprint.view, "user_story_form")

def test_sprint_controller_submit_the_edit_user_story_form_with_errors():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    project_view.sprint.notifier = mock.Mock()
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.EDIT_USER_STORY_OR_TASK)
    form = project_detail_controller.sprint.view.user_story_form

    form._subject_edit.set_edit_text("")
    signals.emit(form.save_button, "click")
    assert project_view.sprint.notifier.error_msg.call_count == 1

def test_sprint_controller_submit_edit_user_story_form_successfully():
    us_subject = "Update a user story"
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    project_view.sprint.notifier = mock.Mock()
    executor = factories.patched_executor(update_user_story_response=factories.future(
                           factories.successful_update_user_story_response(us_subject)))
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.EDIT_USER_STORY_OR_TASK)
    form = project_detail_controller.sprint.view.user_story_form
    project_view.sprint.notifier.reset_mock()

    form._subject_edit.set_edit_text(us_subject)

    signals.emit(form.save_button, "click")
    assert project_view.sprint.notifier.info_msg.call_count == 1
    assert (executor.update_user_story.call_args.call_list()[0][0][0]["id"] == form.user_story["id"])
    assert executor.update_user_story.call_args.call_list()[0][0][1]["subject"] == us_subject
    assert executor.update_user_story.call_count == 1
    assert executor.update_user_story.return_value.result()["subject"] == us_subject

def test_sprint_controller_show_the_milestone_selector_popup():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)

    assert not hasattr(project_detail_controller.view.sprint, "milestone_selector_popup")
    project_detail_controller.handle(config.ProjectBacklogKeys.MOVE_US_TO_MILESTONE)
    assert hasattr(project_detail_controller.view.sprint, "milestone_selector_popup")

def test_sprint_controller_close_the_milestone_selector_popup():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.CHANGE_TO_MILESTONE)

    assert hasattr(project_detail_controller.view.sprint, "milestone_selector_popup")
    milestone_selector_popup = project_detail_controller.view.sprint.milestone_selector_popup
    signals.emit(milestone_selector_popup.cancel_button, "click")
    assert not hasattr(project_detail_controller.view.sprint, "milestone_selector_popup")

def test_sprint_controller_change_to_another_milestone():
    project = factories.project()
    project_view = views.projects.ProjectDetailView(project)
    project_view.sprint.notifier = mock.Mock()
    executor = factories.patched_executor()
    _ = mock.Mock()
    project_detail_controller = controllers.projects.ProjectDetailController(project_view, executor, _)
    project_detail_controller.handle(config.ProjectKeys.MILESTONES)
    project_detail_controller.handle(config.ProjectMilestoneKeys.CHANGE_TO_MILESTONE)
    milestone_selector_popup = project_detail_controller.view.sprint.milestone_selector_popup
    project_view.sprint.notifier.reset_mock()
    executor.milestone.reset_mock()
    executor.milestone_stats.reset_mock()
    executor.user_stories.reset_mock()
    executor.tasks.reset_mock()

    assert project_view.sprint.notifier.info_msg.call_count == 0
    assert executor.milestone.call_count == 0
    assert executor.milestone_stats.call_count == 0
    assert executor.user_stories.call_count == 0
    assert executor.tasks.call_count == 0
    signals.emit(milestone_selector_popup.options[2], "click")
    assert project_view.sprint.notifier.info_msg.call_count == 1
    assert executor.milestone.call_count == 1
    assert executor.milestone_stats.call_count == 1
    assert executor.user_stories.call_count == 1
    assert executor.tasks.call_count == 1
    assert (project_detail_controller.sprint.milestone["id"] ==
            milestone_selector_popup.project["list_of_milestones"][-1]["id"])
