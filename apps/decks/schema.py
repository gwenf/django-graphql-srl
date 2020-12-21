from graphene_django import DjangoObjectType
import graphene

from .models import Deck


class DeckType(DjangoObjectType):
    class Meta:
        model = Deck


class CreateDeck(graphene.Mutation):
    deck = graphene.Field(DeckType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()

    def mutate(self, info, title, description):
        d = Deck(title=title, description=description)
        d.save()
        return CreateDeck(deck=d)
