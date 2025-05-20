from frontend.views.common.text_input import TextInput
from frontend.views.common.boolean_switch import BooleanSwitch
from frontend.views.common.filtered_dropdown import FilteredDropdown
from frontend.views.common.date_picker import DatePickerInput
from frontend.views.common.text_input import TextInput
import importlib
from frontend.utils.colors import get_theme_colors

def update_text_input(edit_fields, key, event):
    if isinstance(event, bool):
        edit_fields[key].value = event
    else:
        edit_fields[key].value = event.control.value

    edit_fields[key].update()

def create_text_input(label, key, instance, theme_mode):
    theme_colors = get_theme_colors(theme_mode)
    return lambda value, on_change: TextInput(
        label=label,
        value=value,
        on_change=lambda e: setattr(instance, f"{key}_value", e.control.value),
        theme_colors=theme_colors
    )

def create_boolean_switch(label, key, instance):
    return lambda value, on_change: BooleanSwitch(
        label=label,
        value=bool(value),
        on_change=lambda e: setattr(instance, f"{key}_value", e.control.value)
    )

def create_date_input(label, key, instance):
    return lambda value, _: DatePickerInput(
        label=label,
        value=value
    )

def create_filtered_dropdown(label, key, endpoint, instance, foreign_key_column, theme_mode):
    return lambda value, on_select: FilteredDropdown(
        label=label,
        on_select=lambda selected: set_selected_value(instance.edit_fields, key, selected),
        endpoint=endpoint,
        id_field="id",
        name_field=foreign_key_column,
        selected_value={"id": value["id"], foreign_key_column: value["name"]} if isinstance(value, dict) else {"id": None, foreign_key_column: ""},
        theme_mode=theme_mode
    )

def set_selected_value(edit_fields, key, selected):
    if key in edit_fields:
        if "name" in selected and "id" in selected:
            edit_fields[key].search_field.value = selected["name"]
            edit_fields[key].selected_id = selected["id"]

        edit_fields[key].update()

def create_date_picker_input(label, key, instance):
    return lambda value, on_change: DatePickerInput(
        label=label,
        key=key,
        parent=instance,
        value=value or ""
    )

def create_number_input(label, key, parent, theme_mode):
    theme_colors = get_theme_colors(theme_mode)
    return lambda value, _: DatePickerInput(
        label=label,
        value=value,
        theme_colors=theme_colors
    )

def load_model_config(endpoint):
    module = importlib.import_module(f"backend.core.models.{endpoint}")
    return module.MODEL_CONFIG


