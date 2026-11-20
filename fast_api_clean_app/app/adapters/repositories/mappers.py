from app.domain.entities.player import Player, PlayerStatus
from app.domain.entities.platform_link import PlatformLink
from app.domain.entities.credential import Credential, CredentialType
from app.domain.value_objects.platform_type import PlatformType
from app.adapters.repositories.models import (
    PlayerModel, PlatformLinkModel, CredentialModel,
)

# ---------- Player ----------

def to_player_entity(model: PlayerModel) -> Player:
    return Player(
        id=model.id,
        display_name=model.display_name,
        email=model.email,
        status=PlayerStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
        platform_links=[
            PlatformLink(
                id=link.id,
                player_id=link.player_id,
                platform=PlatformType(link.platform),
                platform_user_id=link.platform_user_id,
                linked_at=link.linked_at,
                metadata=dict(link.link_metadata or {}),
            )
            for link in model.platform_links
        ],
    )


def to_player_model(entity: Player, model: PlayerModel | None = None) -> PlayerModel:
    if model is None:
        model = PlayerModel(id=entity.id)
    model.display_name = entity.display_name
    model.email = entity.email
    model.status = entity.status.value
    model.created_at = entity.created_at
    model.updated_at = entity.updated_at

    existing_by_id = {link.id: link for link in model.platform_links}
    entity_ids = {link.id for link in entity.platform_links}

    model.platform_links = [
        link_model for link_model in model.platform_links
        if link_model.id in entity_ids
    ]
    for link in entity.platform_links:
        if link.id not in existing_by_id:
            model.platform_links.append(
                PlatformLinkModel(
                    id=link.id,
                    player_id=link.player_id,
                    platform=link.platform.value,
                    platform_user_id=link.platform_user_id,
                    linked_at=link.linked_at,
                    link_metadata=link.metadata,
                )
            )
    return model


# ---------- Credential ----------

def to_credential_entity(model: CredentialModel) -> Credential:
    return Credential(
        id=model.id,
        player_id=model.player_id,
        type=CredentialType(model.type),
        secret_hash=model.secret_hash,
        created_at=model.created_at,
        last_used_at=model.last_used_at,
    )


def to_credential_model(
    entity: Credential, model: CredentialModel | None = None
) -> CredentialModel:
    if model is None:
        model = CredentialModel(id=entity.id)
    model.player_id = entity.player_id
    model.type = entity.type.value
    model.secret_hash = entity.secret_hash
    model.created_at = entity.created_at
    model.last_used_at = entity.last_used_at
    return model
