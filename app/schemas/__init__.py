from .user import UserBase, UserCreate, UserUpdate, UserInDB, UserPublic, UserShort
from .role import RoleBase, RoleCreate, RoleUpdate, RoleInDB, RolePublic, RoleShort
from .os import OperatingSystemBase, OperatingSystemCreate, OperatingSystemUpdate, OperatingSystemInDB, OperatingSystemPublic, OperatingSystemShort
from .environment import EnvironmentBase, EnvironmentCreate, EnvironmentUpdate, EnvironmentInDB, EnvironmentPublic, EnvironmentShort
from .project import ProjectBase, ProjectCreate, ProjectUpdate, ProjectInDB, ProjectPublic, ProjectShort 
from .server import ServerBase, ServerCreate, ServerUpdate, ServerInDB, ServerPublic, ServerShort
from .configuration import ConfigurationBase, ConfigurationCreate, ConfigurationUpdate, ConfigurationInDB, ConfigurationPublic, ConfigurationShort
from .template import TemplateBase, TemplateCreate, TemplateUpdate, TemplateInDB, TemplatePublic, TemplateShort
from .server_template import ServerTemplateBase, ServerTemplateCreate, ServerTemplateUpdate, ServerTemplateInDB, ServerTemplatePublic, ServerTemplateShort, ServerTemplateShortForTemplate
from .server_configuration import ServerConfigurationBase, ServerConfigurationCreate, ServerConfigurationUpdate, ServerConfigurationInDB, ServerConfigurationPublic, ServerConfigurationShort, ServerConfigurationShortForConfiguration, ServerConfigurationShortForExecution
from .template_configuration import TemplateConfigurationBase, TemplateConfigurationCreate, TemplateConfigurationUpdate, TemplateConfigurationInDB, TemplateConfigurationPublic, TemplateConfigurationShort, TemplateConfigurationShortForConfiguration, BulkAttachConfigurationItem, BulkAttachToTemplate
from .execution_group import ExecutionGroupBase, ExecutionGroupCreate, ExecutionGroupUpdate, ExecutionGroupInDB, ExecutionGroupPublic, ExecutionGroupShort
from .execution import ExecutionBase, ExecutionCreate, ExecutionUpdate, ExecutionInDB, ExecutionPublic, ExecutionShort

# ✅ Rebuild après avoir TOUT importé
RolePublic.model_rebuild()
ServerPublic.model_rebuild()
TemplatePublic.model_rebuild()
ConfigurationPublic.model_rebuild()
UserPublic.model_rebuild()
ProjectPublic.model_rebuild()
EnvironmentPublic.model_rebuild()
OperatingSystemPublic.model_rebuild()
ServerTemplatePublic.model_rebuild()
ServerConfigurationPublic.model_rebuild()
TemplateConfigurationPublic.model_rebuild()
ExecutionGroupPublic.model_rebuild()
ExecutionPublic.model_rebuild()
