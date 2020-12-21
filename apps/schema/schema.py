from graphene_django import DjangoObjectType
import graphene

from apps.users.models import User as UserModel
from apps.decks.models import Deck as DeckModel
from apps.cards.models import Card as CardModel


class User(DjangoObjectType):
    class Meta:
        model = UserModel


class Deck(DjangoObjectType):
    class Meta:
        model = DeckModel


class Card(DjangoObjectType):
    class Meta:
        model = CardModel
        # fields = ("deck",)


class CreateCard(graphene.Mutation):
    card = graphene.Field(Card)

    class Arguments:
        question = graphene.String()
        answer = graphene.String()
        deck_id = graphene.Int()

    def mutate(self, info, question, answer, deck_id):
        c = CardModel(question=question, answer=answer)
        d = DeckModel.objects.get(id=deck_id)
        c.deck = d
        c.save()
        return CreateCard(card=c)

        
class CreateDeck(graphene.Mutation):
    deck = graphene.Field(Deck)

    class Arguments:
        title = graphene.String()
        description = graphene.String()

    def mutate(self, info, title, description):
        d = DeckModel(title=title, description=description)
        d.save()
        return CreateDeck(deck=d)


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_deck = CreateDeck.Field()


class Query(graphene.ObjectType):
    users = graphene.List(User)
    decks = graphene.List(Deck)
    decks_by_id = graphene.List(Deck, id=graphene.Int())
    cards = graphene.List(Card)
    deck_cards = graphene.List(Card, deck=graphene.Int())

    def resolve_users(self, info):
        return UserModel.objects.all()

    def resolve_decks(self, info):
        return DeckModel.objects.all()

    def resolve_decks_by_id(self, info, id):
        return DeckModel.objects.get(pk=id)

    def resolve_deck_cards(self, info, deck):
        return CardModel.objects.filter(deck=deck)

    def resolve_cards(self, info):
        return CardModel.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
