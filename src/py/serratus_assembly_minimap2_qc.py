#!/usr/bin/python3

'''
Usage:

	serratus_assembly_minimap2_qc.py hits.sam [acc2desc.tsv] > report.tsv

The SAM file is generated by minimap2 by mapping assemblies
to complete Cov genomes, e.g.:

    minimap2 \
      -x map-pb \
      -t 8 \
      -a \
      -N 1 \
      ../minimap2_index/covref.mmi \
      catA-v3.fa \
      > hits.sam
'''

import sys

def ParseCigar(CIGAR):
	Clip = 0
	QL = 0
	M = 0

	assert CIGAR != "*"

	n = len(CIGAR)
	assert n > 0
	if not CIGAR[0].isdigit():
		print("CIGAR: not C[0].isdigit()", C, CIGAR)
		assert False
	assert CIGAR[n-1].isalpha()

	N = 0
	for c in CIGAR:
		if c.isdigit():
			N = N*10 + (ord(c) - ord('0'))
		elif c.isalpha() or c == '=':
			if c == 'S' or c == 'H':
				QL += N
				Clip += N
			elif c == 'M' or c == "=" or c == "I":
				M += N
				QL += N
			N = 0
		else:
			print("CIGAR: not letter or digit", C, CIGAR)
			assert False
	return QL, Clip, M

def GetQuality():
	if Clip > 1000:
		return "hiclip_suspicious"

	if PctId >= 99.0:
		if LengthDiff > -50 and LengthDiff < 50 and Clip < 50:
			return "complete"
		if LengthDiff > -300 and LengthDiff < 300 and Clip < 300:
			return "near_complete"
		return "partial"

	if PctId >= 97.0:
		if LengthDiff > -150 and LengthDiff < 150 and Clip < 150:
			return "complete"
		if LengthDiff > -500 and LengthDiff < 500 and Clip < 500:
			return "near_complete"
		return "partial"

	return "unknown"

AssToMaxM = {}
AssToBestRec = {}

LabelToLen = {}
LabelToDesc = None

SAMFN = sys.argv[1]
TsvFN = None
if len(sys.argv) > 2:
	LabelToDesc = {}
	TsvFN = sys.argv[2]
	for Line in open(TsvFN):
		Fields = Line[:-1].split('\t')
		Label = Fields[0].split(".")[0]
		Desc = Fields[1]
		LabelToDesc[Label] = Desc

f = open(SAMFN)
for Line in f:
	# @SQ     SN:NC_038294.1  LN:30111
	if Line.startswith("@SQ"):
		Fields = Line.split()
		assert Fields[0] == "@SQ"
		assert Fields[1].startswith("SN:")
		assert Fields[2].startswith("LN:")
		Label = Fields[1][3:]
		Len = int(Fields[2][3:])
		LabelToLen[Label] = Len
		continue

	if Line.startswith('@'):
		continue
	Fields = Line[:-1].split('\t')
	QueryLabel = Fields[0]
	Flags = int(Fields[1])
	RefLabel = Fields[2]
	Pos = Fields[3]
#	MAPQ = Fields[4]
	CIGAR = Fields[5]
#	RNEXT = Fields[6]
#	PNEXT = Fields[7]
#	TLEN = int(Fields[8]) # always zero?
	# SEQ = Fields[9]
	Tags = Fields[11:]

	TLEN = LabelToLen[RefLabel]

	Ass = QueryLabel.split('.')[0]

	Diffs = None
	for Tag in Tags:
		if Tag.startswith("NM:i:"):
			Diffs = int(Tag[5:])
			break
	assert Diffs != None

	if (Flags & 0x10) == 0x10:
		Strand = "-"
	else:
		Strand = "+"

	QL, Clip, M = ParseCigar(CIGAR)
	LengthDiff = TLEN - QL - Clip
	PctId = 100.0 - (Diffs*100.0)/QL
	PctClip = (Clip*100.0)/QL

	Quality = GetQuality()
	Acc = RefLabel.split(".")[0]
	Desc = LabelToDesc[Acc]
	try:
		Desc = LabelToDesc[Acc]
	except:
		Desc = None

	Rec = Ass
	Rec += "\t" + Quality
	Rec += "\t%u" % Clip
	Rec += "\t%.1f" % PctClip
	Rec += "\t%u" % QL
	Rec += "\t%+d" % LengthDiff
	Rec += "\t" + Strand
	Rec += "\t" + RefLabel
	Rec += "\t%u" % TLEN
	Rec += "\t%u" % Diffs
	Rec += "\t%.1f" % PctId
	if Desc != None:
		Rec += "\t" + Desc

	try:
		m = AssToMaxM[Ass]
	except:
		m = -1
	if M > m:
		AssToMaxM[Ass] = M
		AssToBestRec[Ass] = Rec

for Ass in list(AssToBestRec.keys()):
	Rec = AssToBestRec[Ass]
	print(Rec)
