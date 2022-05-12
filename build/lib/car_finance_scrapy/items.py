# -*- coding: utf-8 -*-
__all__ = [
	'CarItem'
]

from scrapy import Item, Field
from .processors import *

class CarItem(Item):
	CarMake = Field()
	CarModel = Field()
	TypeofFinance = Field()
	MonthlyPayment = Field()
	CustomerDeposit = Field()
	RetailerDepositContribution = Field()
	OnTheRoadPrice = Field()
	AmountofCredit = Field()
	DurationofAgreement  = Field()
	OptionalPurchase_FinalPayment = Field()
	TotalAmountPayable = Field()
	OptionToPurchase_PurchaseActivationFee = Field()
	RepresentativeAPR = Field()
	FixedInterestRate_RateofinterestPA = Field()
	ExcessMilageCharge = Field()
	AverageMilesPerYear = Field()
	OfferExpiryDate = Field()
	RetailCashPrice = Field()
	WebpageURL = Field()
	CarimageURL = Field()
	FinalPaymentPercent = Field()
	DepositPercent = Field()
	DebugMode = Field()
	# FinalPayment = Field()
