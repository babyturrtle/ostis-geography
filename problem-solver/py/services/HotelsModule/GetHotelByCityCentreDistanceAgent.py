from termcolor import colored

from common import ScAgent, ScEventParams, ScKeynodes
from sc import *


class GetHotelByCityCentreDistanceAgent(ScAgent):
    def __init__(self, module):
        super().__init__(module)
        self.ctx = module.ctx
        self.keynodes = ScKeynodes(self.ctx)
        self.main_node = None

    def RunImpl(self, evt: ScEventParams) -> ScResult:
        self.main_node = evt.other_addr
        status = ScResult.Ok

        if self.module.ctx.HelperCheckEdge(
                self.keynodes['action_get_hotel_by_city_centre_distance'],
                self.main_node,
                ScType.EdgeAccessConstPosPerm,
        ):
            try:
                if self.main_node is None or not self.main_node.IsValid():
                    raise Exception("The question node isn't valid.")
                node = self.get_action_argument(self.main_node, 'rrel_1') 
                answerNode = self.ctx.CreateNode(ScType.NodeConstStruct)
                self.add_nodes_to_answer(answerNode, [node])

                hotelIterator = self.ctx.Iterator5(
                    ScType.Unknown,
                    ScType.EdgeDCommon,
                    node,
                    ScType.EdgeAccessConstPosPerm,
                    self.keynodes['nrel_city_centre_distance']
                )
                while hotelIterator.Next():
                    hotel = hotelIterator.Get(0)
                    hotelcheck = False
                    checkIterator = self.ctx.Iterator3(
                        self.keynodes['concept_hotel'],
                        ScType.EdgeAccessConstPosPerm,
                        hotel
                    )
                    if checkIterator.Next():
                        hotelcheck = True
                    
                    if hotelcheck == True:
                        checkIterator = self.ctx.Iterator3(
                            self.keynodes['concept_map_object'],
                            ScType.EdgeAccessConstPosPerm,
                            hotel
                        )
                        if checkIterator.Next():
                            self.add_nodes_to_answer(answerNode, [hotel, hotelIterator.Get(1), hotelIterator.Get(3), hotelIterator.Get(4)])
                        else:
                            print("It is not a hotel")
					
                self.finish_agent(self.main_node, answerNode)
            except Exception as ex:
                print(colored(str(ex), color='red'))
                self.set_unsuccessful_status()
                status = ScResult.Error
            finally:
                self.ctx.CreateEdge(
                    ScType.EdgeAccessConstPosPerm,
                    self.keynodes['question_finished'],
                    self.main_node,
                )
        return status

    def set_unsuccessful_status(self):
        self.module.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm,
            self.keynodes['question_finished_unsuccessfully'],
            self.main_node,
        )

    def finish_agent(self, action_node, answer):
        contour_edge = self.ctx.CreateEdge(
            ScType.EdgeDCommonConst,
            action_node,
            answer
        )
        self.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm,
            self.keynodes['nrel_answer'],
            contour_edge
        )
        self.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm,
            self.keynodes['question_finished_successfully'],
            action_node,
        )

    def get_action_argument(self, question: ScAddr, rrel: str, argument_class=None) -> ScAddr:
        actual_argument = "_actual_argument"

        keynodes = self.keynodes

        template = ScTemplate()
        template.TripleWithRelation(
            question,
            ScType.EdgeAccessVarPosPerm,
            ScType.NodeVar >> actual_argument,
            ScType.EdgeAccessVarPosPerm,
            keynodes[rrel],
        )
        if argument_class is not None:
            template.Triple(keynodes[argument_class], ScType.EdgeAccessVarPosPerm, actual_argument)

        search_result = self.ctx.HelperSearchTemplate(template)

        search_result_size = search_result.Size()
        if search_result_size > 0:
            argument_node = search_result[0][actual_argument]
        else:
            raise Exception("The argument node isn't found.")

        return argument_node

    def add_nodes_to_answer(self, contour=None, nodes=None):
        if contour is None:
            contour = self.ctx.CreateNode()
        if nodes is None:
            nodes = []
        for node in nodes:
            self.ctx.CreateEdge(
                ScType.EdgeAccessConstPosPerm,
                contour,
                node
            )
