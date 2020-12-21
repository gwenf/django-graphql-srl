from django.utils import timezone

from graphene_django import DjangoObjectType
import graphene
from graphql import GraphQLError

from .models import Card
from apps.decks.models import Deck

from apps.decks.schema import (
    CreateDeck,
    DeckType
)

buckets = (
    (1, 1),
    (2, 3),
    (3, 7),
    (4, 16),
    (5, 30),
)

def return_date_time(days):
    now = timezone.now()
    return now + timezone.timedelta(days=days)


class CardType(DjangoObjectType):
    class Meta:
        model = Card
        # fields = ("deck",)


class CreateCard(graphene.Mutation):
    card = graphene.Field(CardType)

    class Arguments:
        question = graphene.String()
        answer = graphene.String()
        deck_id = graphene.Int()

    def mutate(self, info, question, answer, deck_id):
        c = Card(question=question, answer=answer)
        d = Deck.objects.get(id=deck_id)
        c.deck = d
        c.save()
        return CreateCard(card=c)


class UpdateCard(graphene.Mutation):
    card = graphene.Field(CardType)

    class Arguments:
        id = graphene.ID()
        question = graphene.String()
        answer = graphene.String()
        # easy, average, or difficult -> 1, 2, 3
        status = graphene.Int(description="easy, average, or difficult -> 1, 2, 3")

    def mutate(self, info, id, question, answer, status):
        if status not in [1,2,3]:
            raise GraphQLError('Status out of bounds. Must be 1, 2, or 3.')

        c = Card.objects.get(id=id)

        bucket = c.bucket
        if status == 1 and bucket > 1:
            bucket -= 1
        elif status == 3 and bucket <= 4:
            bucket += 1

        # Calculate next review at date
        days = buckets[bucket-1][1]
        next_review_at = return_date_time(days)

        c.question = question
        c.answer = answer
        c.bucket=bucket
        c.next_review_at=next_review_at
        c.last_reviewed_at=timezone.now()
        c.save()

        return UpdateCard(card=c)
