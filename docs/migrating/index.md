# Migrating

## From `anvil_extras.routing` (`HashRouting`)

There is no clear migration path from `HashRouting` to `routing`. One major obstacle for migration is that `HashRouting` keeps the template the same and changes the component of the template's `content_panel`. `routing` calls `anvil.open_form` on the matching route's form.

