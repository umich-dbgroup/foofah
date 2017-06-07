#include <iostream>
#include <tuple>
#include <cstring>         // std::string
#include <limits>
#include <string>
#include <stdlib.h>
#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <set>
#include <map>
#include <vector>
// #include <TableGraph.cpp>

using namespace boost::python;

using namespace std;

const int MAP_TYPE_MV = 1;
const int MAP_TYPE_MER = 2;
const int MAP_TYPE_SPL = 3;
const int MAP_TYPE_UNKNOWN = 4;
const int MAP_TYPE_RM = 5;
const int MAP_TYPE_ADD = 6;

const double COST_IMPOSSIBLE = 10000;

const double COST_DELETE_EXISTING_CELL = 1;
const double COST_DELETE_CELL = 1;
const double COST_DELETE_EMPTY = 1;
const double COST_ADD_EMPTY = 1;
const double COST_MOVE_EMPTY = 1;
const double COST_MOVE_CELL = 1;
const double COST_SPLIT = 1;
const double COST_MERGE = 1;
const double COST_COPY = 1;


const int IF_CACHE = true;

#include <string>
#include <boost/tokenizer.hpp>
#include <vector>

using namespace std;
using namespace boost;


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
 
#define ARRAY_SIZE(a) sizeof(a)/sizeof(a[0])
 
// Alphabet size (# of symbols)
#define ALPHABET_SIZE (26)
 
// Converts key current character into index
// use only 'a' through 'z' and lower case
#define CHAR_TO_INDEX(c) ((int)c - (int)'a')
 
#include <iostream>
#include <vector>
using namespace std;


// Code borrowed from: http://www.sourcetricks.com/2011/06/c-tries.html#.V9rSl3UrKpc

class Node {
public:
    Node() { mContent = ' '; mMarker = false; }
    ~Node() {}
    char content() { return mContent; }
    void setContent(char c) { mContent = c; }
    bool wordMarker() { return mMarker; }
    void setWordMarker() { mMarker = true; }
    Node* findChild(char c);
    void appendChild(Node* child) { mChildren.push_back(child); }
    vector<Node*> children() { return mChildren; }

private:
    char mContent;
    bool mMarker;
    vector<Node*> mChildren;
};

class Trie {
public:
    Trie();
    ~Trie();
    void addWord(string s);
    bool searchWord(string s);
    void deleteWord(string s);
private:
    Node* root;
};

Node* Node::findChild(char c)
{
    for ( int i = 0; i < mChildren.size(); i++ )
    {
        Node* tmp = mChildren.at(i);
        if ( tmp->content() == c )
        {
            return tmp;
        }
    }

    return NULL;
}

Trie::Trie()
{
    root = new Node();
}

Trie::~Trie()
{
    // Free memory
}

void Trie::addWord(string s)
{
    Node* current = root;

    if ( s.length() == 0 )
    {
        current->setWordMarker(); // an empty word
        return;
    }

    for ( int i = 0; i < s.length(); i++ )
    {        
        Node* child = current->findChild(s[i]);
        if ( child != NULL )
        {
            current = child;
        }
        else
        {
            Node* tmp = new Node();
            tmp->setContent(s[i]);
            current->appendChild(tmp);
            current = tmp;
        }
        if ( i == s.length() - 1 )
            current->setWordMarker();
    }
}


bool Trie::searchWord(string s)
{
    Node* current = root;

    while ( current != NULL )
    {
        for ( int i = 0; i < s.length(); i++ )
        {
            Node* tmp = current->findChild(s[i]);
            if ( tmp == NULL )
                return false;
            current = tmp;
        }

        if ( current->wordMarker() )
            return true;
        else
            return false;
    }

    return false;
}



std::vector<string> tokenize(string text)
{

    char_separator<char> sep(", !@#$%^&*()-_=+.<>?/;:'\"[{}]|\\~`\t");
    tokenizer<char_separator<char>> tokens(text, sep);

    size_t size = std::distance(tokens.begin(), tokens.end());

    std::vector<string> tk_vector(size);

    int i = 0;

    for(boost::tokenizer< boost::char_separator<char> >::iterator beg = tokens.begin(); beg != tokens.end(); ++beg)
	{
	     tk_vector[i] = *beg;
        i++; 
	}


    return tk_vector;
}

bool ifIntersect(std::vector<string> set1, std::vector<string> set2){
	for(string tok1 : set1){
			for(string tok2 : set2){
				if(tok2.compare(tok1)==0){
					return true;
				}
			} 
		} 

	return false;

}

std::map<std::pair<string,string>, boost::tuple<int,int>> cache_c;

boost::tuple<int,int> cost_data_transform_c(const string str1, const string str2) {

    if(IF_CACHE && cache_c.find(std::make_pair(str1, str2)) != cache_c.end()){
		return cache_c[std::make_pair(str1, str2)];
	}
    else if(str1.compare(str2) == 0){
    	if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(0,MAP_TYPE_MV);
		return boost::make_tuple(0,MAP_TYPE_MV);
    }
	else if(str1.length()==0 || str2.length()==0){
		if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
		return boost::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
	}
	else if (str1.find(str2) != std::string::npos){
		if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_MERGE,MAP_TYPE_MER);
		return boost::make_tuple(COST_MERGE,MAP_TYPE_MER);
	}
	else if (str2.find(str1) != std::string::npos){
		if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_SPLIT,MAP_TYPE_SPL);
		return boost::make_tuple(COST_SPLIT,MAP_TYPE_SPL);
	}

	else{
		std::vector<string> token_1 = tokenize(str1);
		std::vector<string> token_2 = tokenize(str2);


		for(string tok1 : token_1){
			if(str2.find(tok1) != std::string::npos){
					if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
					return boost::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
				}
			
		} 

		for(string tok2 : token_2){
				if(str1.find(tok2) != std::string::npos){
					if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
					return boost::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
				}
			} 

		if(IF_CACHE) cache_c[std::make_pair(str1, str2)] = boost::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
		return boost::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
	
	}

}




std::map<std::pair<string,string>, boost::python::tuple> cache;


boost::python::tuple cost_data_transform(const string str1, const string str2 ) {
	// cout<<cache[std::make_pair(str1, str2)];

	if(IF_CACHE && cache.find(std::make_pair(str1, str2)) != cache.end()){
		return cache[std::make_pair(str1, str2)];
	}
	else if(str1.compare(str2) == 0){
		if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(0,MAP_TYPE_MV);
		return boost::python::make_tuple(0,MAP_TYPE_MV);
    }
	else if(str1.length()==0||str2.length()==0){
		if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
		return boost::python::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
	}
	else if (str2.find(str1) != std::string::npos){
		if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_MERGE,MAP_TYPE_MER);
		return boost::python::make_tuple(COST_MERGE,MAP_TYPE_MER);
	}
	else if (str1.find(str2) != std::string::npos){
		if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_SPLIT,MAP_TYPE_SPL);
		return boost::python::make_tuple(COST_SPLIT,MAP_TYPE_SPL);
	}

	else{

		std::vector<string> token_1 = tokenize(str1);
		std::vector<string> token_2 = tokenize(str2);

		bool notFound1 = false;
		bool notFound2 = false;

		for(string tok1 : token_1){
			if(str2.find(tok1) != std::string::npos){
				
				if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
				return boost::python::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
		
			}
			
		} 

		for(string tok2 : token_2){
			if(str1.find(tok2) != std::string::npos){
				// if(str1=="Subject 2"&&str2=="Subject2") cout<<"WTF\n";
				if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
				return boost::python::make_tuple(COST_SPLIT+COST_MERGE,MAP_TYPE_UNKNOWN);
		
			}
		} 

		// if(notFound1==false||notFound2==false){ 
		// 	}
		// cout<<str1<<"&"<<str2<<"\n";
		if(IF_CACHE) cache[std::make_pair(str1, str2)] = boost::python::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
		return boost::python::make_tuple(COST_IMPOSSIBLE,MAP_TYPE_UNKNOWN);
	
	}

}


double cost_move(const int row_1,const int col_1,const int row_2,const int col_2,const string data_1){

	double cost = 0;

	if(data_1.length() > 0){
		// Move row or col
		if(row_1 != row_2 || col_1 != col_2){
			cost = cost + COST_MOVE_CELL;

		}

	}
	else if(row_1 != row_2 || col_1 != col_2) {
		cost = cost + COST_MOVE_EMPTY;
	}

	return cost;
}



boost::python::tuple cost_edit_op(int u_row, int u_col, string u_data, int v_row, int v_col, string v_data){

	float cost = 0;
	int map_type = 0;

	// print operation
	if(u_row != -1 && v_row != -1){
		boost::tuple<int, int> l = cost_data_transform_c(u_data,v_data);

		int new_cost = l.get<0>();
		map_type = l.get<1>();

		cost += new_cost;

		if(cost >= COST_IMPOSSIBLE){
			return boost::python::make_tuple(cost,map_type);
		}


		cost += cost_move(u_row,u_col,v_row,v_col,u_data);

	}
	else if(u_row != -1 && u_data.length() > 0){
		cost += COST_DELETE_CELL;
		map_type = MAP_TYPE_RM;
	}

	else if(u_row != -1 && u_data.length() <= 0){
		cost += COST_DELETE_EMPTY;
		map_type = MAP_TYPE_RM;
	}
	else if(v_row != -1 && v_data.length()>0){
		cost += COST_IMPOSSIBLE;
		map_type = MAP_TYPE_ADD;
	}
	else{
		cost += COST_ADD_EMPTY;
		map_type = MAP_TYPE_ADD;
	}

	return boost::python::make_tuple(cost,map_type);

}


boost::tuple<float, int> cost_edit_op_c(int u_row, int u_col, string u_data, int v_row, int v_col, string v_data){

	float cost = 0;
	int map_type = 0;

	// print operation
	if(u_row != -1 && v_row != -1){
		boost::tuple<float, int>  l = cost_data_transform_c(u_data,v_data);

		float new_cost = l.get<0>();
		map_type = l.get<1>();

		cost += new_cost;

		if(cost >= COST_IMPOSSIBLE){
			return l;
		}


		cost += cost_move(u_row,u_col,v_row,v_col,u_data);

	}
	else if(u_row != -1 && u_data.length() > 0){
		cost += COST_DELETE_CELL;
		map_type = MAP_TYPE_RM;
	}

	else if(u_row != -1 && u_data.length() <= 0){
		cost += COST_DELETE_EMPTY;
		map_type = MAP_TYPE_RM;
	}
	else if(v_row != -1 && v_data.length()>0){
		cost += COST_IMPOSSIBLE;
		map_type = MAP_TYPE_ADD;
	}
	else{
		cost += COST_ADD_EMPTY;
		map_type = MAP_TYPE_ADD;
	}

	boost::tuple<float, int>  result = boost::make_tuple(cost,map_type);

	return result;

}


class TableNode{
public:
	int row;
	int col;
	string data;
	// static long curId;
	long id;
	TableNode();
	TableNode(int row, int col, string data);
	bool operator==(const TableNode &other);
};

TableNode::TableNode(int row, int col,string data){
	this->row = row;
	this->col = col;
	this->data = data;
	this->id = -1;
	// id = curId;
	// TableNode::curId++;
}
// empty node
TableNode::TableNode(){
	this->row = -1;
	this->col = -1;
	this->data = "";
	this->id = -1;
}

bool TableNode::operator==(const TableNode &other){
    if(this->row!=other.row){
    	return false;
    }
    else if(this->col!=other.col){
    	return false;
    }
    else if(this->data != other.data){
    	return false;
    }
    return true;
}


// std::set<string> target_set;

class TableGraph{
public:
	std::vector<TableNode> cells;
	int num_rows;
	int num_cols;

	TableGraph();
	TableGraph(int num_rows,int num_cols);
	void printTable();
	void addCell(string cellStr , int row, int col);
	int size();
};

TableGraph::TableGraph(){
	this->num_rows = 0;
	this->num_cols = 0;
	this->cells.clear();
}


TableGraph::TableGraph(int num_rows,int num_cols){
	// Cells is set to "size"
	// cells.resize(num_rows*num_cols);
	this->num_rows = num_rows;
	this->num_cols = num_cols;
	this->cells.clear();
}

int TableGraph::size(){
	return cells.size();
}

void TableGraph::addCell(string cellStr , int row, int col){

	TableNode newCell(row,col,cellStr);
	// cout<<cellStr<<"######"<<newCell.data<<"\n";
	cells.push_back(newCell);
}

void TableGraph::printTable(){
	for(TableNode n : cells){
		cout<<n.data<<"("<<n.row<<","<<n.col<<")\n";
	}
}


void printEditOp(boost::tuple<TableNode,TableNode,int,float> editOp){
	TableNode a = editOp.get<0>();
	TableNode b = editOp.get<1>();
	if(a.row==-1){
		cout<<"empty -> "<<b.data<<"("<<b.row<<","<<b.col<<")\n";
	}
	else if(b.row==-1){
		cout<<a.data<<"("<<a.row<<","<<a.col<<") -> "<<"empty\n";
	}
	else{
		cout<<a.data<<"("<<a.row<<","<<a.col<<") -> "<<b.data<<"("<<b.row<<","<<b.col<<")\n";

	}

}

void printPath(std::vector<boost::tuple<TableNode,TableNode,int,float>> path){
	for(boost::tuple<TableNode,TableNode,int,float> editOp:path){
		printEditOp(editOp);
	}

}

void remove(std::vector<TableNode> & u, TableNode val){
	int pos = find(u.begin(), u.end(), val) - u.begin();
	if(pos < u.size()) {
	    u.erase(u.begin()+pos);
	}
}

boost::tuple<float,std::vector<boost::tuple<TableNode,TableNode,int,float>>> graph_edit_distance_greedy(TableGraph a, TableGraph b){

	// cout<<"input: "<<a.num_rows<<","<<a.num_cols;
	// cout<<"output: "<<b.num_rows<<","<<b.num_cols;

	std::vector<boost::tuple<TableNode,TableNode,int,float>> chosen_path;
	float chosen_path_cost = 0;


	std::vector<TableNode> u = a.cells;
	std::vector<TableNode> v = b.cells;

	TableNode v0 = v.front();

	std::vector<boost::tuple<TableNode,TableNode,int,float>> possible_path;
	std::vector<int> possible_path_cost;

	bool if_exact_match_found = false;

	for(TableNode w : u){
		boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,v0.row,v0.col,v0.data);

		float new_cost = l.get<0>();
		int map_type = l.get<1>();

		if(map_type==MAP_TYPE_MV){
			if_exact_match_found = true;
		}

		possible_path.push_back(boost::make_tuple(w,v0,map_type,new_cost));
		possible_path_cost.push_back(new_cost);

	}


	// Add empty -> v0
	TableNode w = TableNode();

	boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,v0.row,v0.col,v0.data);
	float new_cost = l.get<0>();
	int map_type = l.get<1>();

	possible_path.push_back(boost::make_tuple(w,v0,map_type,new_cost));
	possible_path_cost.push_back(new_cost);

	

	// Get edit operation with minimum cost as well as the index of this operation
	std::vector<int>::iterator minValuePtr = std::min_element(possible_path_cost.begin(),possible_path_cost.end());

	int minValue = *minValuePtr;
	int path_idx = distance(possible_path_cost.begin(),minValuePtr);

	


	// If there is exact matching found and edit operation with min value is not a move, try second min value
	while(if_exact_match_found==true&&possible_path[path_idx].get<2>() != MAP_TYPE_MV){
		if(possible_path.size()>1){
			possible_path.erase(possible_path.begin()+path_idx);
			possible_path_cost.erase(possible_path_cost.begin()+path_idx);
			
			std::vector<int>::iterator minValuePtr = std::min_element(possible_path_cost.begin(),possible_path_cost.end());

			minValue = *minValuePtr;
			path_idx = distance(possible_path_cost.begin(),minValuePtr);
		}
		else{
			break;
		}
	}

	chosen_path.push_back(possible_path.at(path_idx));
	chosen_path_cost += possible_path_cost.at(path_idx);


	
	// Remove these nodes
	// u.erase(u.begin()+path_idx);

	remove(u, possible_path[path_idx].get<0>());

	v.erase(v.begin()+0);


	// Iterate through all nodes

	while(u.size()>0 && v.size()>0){
		TableNode v_next = v.front();
		v.erase(v.begin()+0);

		std::vector<boost::tuple<TableNode,TableNode,int,float>> possible_path;
		std::vector<int> possible_path_cost;

		bool if_exact_match_found = false;

		for(TableNode w : u){
			boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,v_next.row,v_next.col,v_next.data);

			float new_cost = l.get<0>();
			int map_type = l.get<1>();

			if(map_type==MAP_TYPE_MV){
				if_exact_match_found = true;
			}

			possible_path.push_back(boost::make_tuple(w,v_next,map_type,new_cost));
			possible_path_cost.push_back(new_cost);

		}
		// Add empty -> v_next
		TableNode none = TableNode();

		boost::tuple<float, int>  l = cost_edit_op_c(none.row,none.col,none.data,v_next.row,v_next.col,v_next.data);
		float new_cost = l.get<0>();
		int map_type = l.get<1>();

		possible_path.push_back(boost::make_tuple(none,v_next,map_type,new_cost));
		possible_path_cost.push_back(new_cost);

		std::vector<int>::iterator minValuePtr = std::min_element(possible_path_cost.begin(),possible_path_cost.end());

		int minValue = *minValuePtr;
		int path_idx = distance(possible_path_cost.begin(),minValuePtr);

		// If there is exact matching found and edit operation with min value is not a move, try second min value
		while(if_exact_match_found==true&&possible_path[path_idx].get<2>() != MAP_TYPE_MV){
			if(possible_path.size()>1){
				possible_path.erase(possible_path.begin()+path_idx);
				possible_path_cost.erase(possible_path_cost.begin()+path_idx);
				
				std::vector<int>::iterator minValuePtr = std::min_element(possible_path_cost.begin(),possible_path_cost.end());

				minValue = *minValuePtr;
				path_idx = distance(possible_path_cost.begin(),minValuePtr);
			}
			else{
				break;
			}
		}


		int tempType = possible_path[path_idx].get<2>();
		if(tempType == MAP_TYPE_UNKNOWN || tempType == MAP_TYPE_SPL || tempType == MAP_TYPE_MER){
			std::vector<boost::tuple<TableNode,TableNode,int,float>> new_possible_path;
			std::vector<int> new_possible_path_cost;

			std::vector<TableNode> u_tot = a.cells;

			for(TableNode w : u_tot){
				boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,v_next.row,v_next.col,v_next.data);

				float new_cost = l.get<0>();
				int map_type = l.get<1>();

				if(map_type==MAP_TYPE_MV){
					if_exact_match_found = true;
				}

				new_possible_path.push_back(boost::make_tuple(w,v_next,map_type,new_cost));
				new_possible_path_cost.push_back(new_cost);

			}


			std::vector<int>::iterator minValuePtr = std::min_element(new_possible_path_cost.begin(),new_possible_path_cost.end());

			int new_minValue = *minValuePtr;
			int new_path_idx = distance(new_possible_path_cost.begin(),minValuePtr);

			// See which edit operation to choose
			if(new_minValue<minValue){
				chosen_path.push_back(new_possible_path.at(new_path_idx));
				chosen_path_cost += new_possible_path_cost.at(new_path_idx);

			}
			else{
				chosen_path.push_back(possible_path.at(path_idx));
				chosen_path_cost += possible_path_cost.at(path_idx);

				// Remove these nodes

				remove(u, possible_path[path_idx].get<0>());



			}

		
		}
		else{
			chosen_path.push_back(possible_path.at(path_idx));
			chosen_path_cost += possible_path_cost.at(path_idx);

			// Remove these nodes
			remove(u, possible_path[path_idx].get<0>());


		}

	}

	if(u.size()<=0 && v.size()>0){
		

		std::vector<TableNode> u_tot = a.cells;
		for(TableNode v_next:v){
			std::vector<boost::tuple<TableNode,TableNode,int,float>> new_possible_path;
			std::vector<int> new_possible_path_cost;
			for(TableNode w : u_tot){
				boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,v_next.row,v_next.col,v_next.data);

				float new_cost = l.get<0>();
				int map_type = l.get<1>();

				if(map_type==MAP_TYPE_MV){
					if_exact_match_found = true;
				}

				new_possible_path.push_back(boost::make_tuple(w,v_next,map_type,new_cost));
				new_possible_path_cost.push_back(new_cost);

			}

			std::vector<int>::iterator minValuePtr = std::min_element(new_possible_path_cost.begin(),new_possible_path_cost.end());

			int new_minValue = *minValuePtr;
			int new_path_idx = distance(new_possible_path_cost.begin(),minValuePtr);
			chosen_path.push_back(new_possible_path.at(new_path_idx));
			chosen_path_cost += new_possible_path_cost.at(new_path_idx);
		}


	
	}

	if(u.size()>0 && v.size()<=0){
		for(TableNode w : u){
			TableNode none = TableNode();

			boost::tuple<float, int>  l = cost_edit_op_c(w.row,w.col,w.data,none.row,none.col,none.data);
			float new_cost = l.get<0>();
			int map_type = l.get<1>();

			chosen_path.push_back(boost::make_tuple(w,none,map_type,new_cost));
			chosen_path_cost += new_cost;

		}
	}

	// printPath(chosen_path);
	return boost::make_tuple<float,std::vector<boost::tuple<TableNode,TableNode,int,float>>>(chosen_path_cost,chosen_path);
}


float get_ged(TableGraph a, TableGraph b){
	boost::tuple<float,std::vector<boost::tuple<TableNode,TableNode,int,float>>>  l = graph_edit_distance_greedy(a,b);
	return l.get<0>();
}

bool in_row_out_row (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	if(get<0>(lhs)!=get<0>(rhs)){
		return get<0>(lhs) < get<0>(rhs);
	}
	else if (get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else if (get<2>(lhs)!=get<2>(rhs)){
		return get<2>(lhs) < get<2>(rhs);
	}
	else{
		return get<3>(lhs) < get<3>(rhs);
	}
}

bool in_row_out_col (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	if(get<0>(lhs)!=get<0>(rhs)){
		return get<0>(lhs) < get<0>(rhs);
	}
	else if (get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else if (get<3>(lhs)!=get<3>(rhs)){
		return get<3>(lhs) < get<3>(rhs);
	}
	else{
		return get<2>(lhs) < get<2>(rhs);
	}
}

bool in_col_out_row (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	if(get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else if (get<0>(lhs)!=get<0>(rhs)){
		return get<0>(lhs) < get<0>(rhs);
	}
	else if (get<2>(lhs)!=get<2>(rhs)){
		return get<2>(lhs) < get<2>(rhs);
	}
	else{
		return get<3>(lhs) < get<3>(rhs);
	}
}


bool out_row_in_col (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	
	if (get<2>(lhs)!=get<2>(rhs)){
		return get<2>(lhs) < get<2>(rhs);
	}
	else if(get<3>(lhs)!=get<3>(rhs)){
		return get<3>(lhs) < get<3>(rhs);
	}
	else if(get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else{
		return get<0>(lhs) < get<0>(rhs);
	}
}

bool in_col_out_col (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	if(get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else if (get<0>(lhs)!=get<0>(rhs)){
		return get<0>(lhs) < get<0>(rhs);
	}
	else if (get<3>(lhs)!=get<3>(rhs)){
		return get<3>(lhs) < get<3>(rhs);
	}
	else{
		return get<2>(lhs) < get<2>(rhs);
	}
}


bool out_col_in_col (const std::tuple<int,int,int,int> &lhs, const std::tuple<int,int,int,int> &rhs){
  	
	if (get<3>(lhs)!=get<3>(rhs)){
		return get<3>(lhs) < get<3>(rhs);
	}
	else if(get<2>(lhs) != get<2>(rhs)){
		return get<2>(lhs) < get<2>(rhs);
	}
	else if(get<1>(lhs)!=get<1>(rhs)){
		return get<1>(lhs) < get<1>(rhs);
	}
	else{
		return get<0>(lhs) < get<0>(rhs);
	}
}



bool check_ajacent(std::tuple<int,int,int,int> a,std::tuple<int,int,int,int> b,int input_down,int input_right, int output_down, int output_right){
	if(get<0>(a) != get<0>(b)+input_down){
		return false;
	}
	else if(get<1>(a) != get<1>(b)+input_right){
		return false;
	}
	else if(get<2>(a) != get<2>(b)+output_down){
		return false;
	}
	else if(get<3>(a) != get<3>(b)+output_right){
		return false;
	}
	return true;
}

bool larger_size(const std::vector<std::tuple<int,int,int,int>>& lhs, const std::vector<std::tuple<int,int,int,int>>& rhs){
  	
	return lhs.size() > rhs.size();
}

bool CheckCommon(std::vector<std::tuple<int,int,int,int>>const& inVectorA, std::vector<std::tuple<int,int,int,int>> const& nVectorB)
{
    return std::find_first_of(inVectorA.begin(), inVectorA.end(),
                               nVectorB.begin(), nVectorB.end()) != inVectorA.end();
}



float get_ged_batch(TableGraph a, TableGraph b, int debug_level){
	boost::tuple<float,std::vector<boost::tuple<TableNode,TableNode,int,float>>>  l = graph_edit_distance_greedy(a,b);
	std::vector<boost::tuple<TableNode,TableNode,int,float>> path = l.get<1>();

	std::map<std::tuple<int,int,int,int>,boost::tuple<TableNode,TableNode,int,float>>  pathMap;

	std::map<int,std::vector<std::tuple<int,int,int,int>>> groupedPath;

	std::vector<std::vector<std::tuple<int,int,int,int>>> potentialBatches;

	std::vector<std::tuple<int,int,int,int>> in_out_total;

	// Collect geometric information of each edit op
	for(boost::tuple<TableNode,TableNode,int,float> t:path){
		TableNode a = t.get<0>();
		TableNode b = t.get<1>();
		pathMap[std::make_tuple(a.row,a.col,b.row,b.col)] = t;


		int editOpType = t.get<2>();
		groupedPath[editOpType].push_back(std::make_tuple(a.row,a.col,b.row,b.col));
		in_out_total.push_back(std::make_tuple(a.row,a.col,b.row,b.col));
	}



	for(std::map<int,std::vector<std::tuple<int,int,int,int>>>::iterator it = groupedPath.begin(); it != groupedPath.end(); it++){
		int editOpType = it->first;
		std::vector<std::tuple<int,int,int,int>> input_output_set = it->second;

		if(editOpType == MAP_TYPE_MV || editOpType == MAP_TYPE_MER || editOpType == MAP_TYPE_SPL || editOpType == MAP_TYPE_UNKNOWN){
			

			// Horizontal to Horizontal
			sort(input_output_set.begin(),input_output_set.end(),in_row_out_row);

			std::vector<std::tuple<int,int,int,int>> temp_path;
			temp_path.push_back(input_output_set[0]);

			std::tuple<int,int,int,int> base = input_output_set[0];

			int i = 1;
			int dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,0,dist,0,dist)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}

			// One to Horizontal
			if(editOpType != MAP_TYPE_SPL && editOpType != MAP_TYPE_MER){

				temp_path.clear();
				temp_path.push_back(input_output_set[0]);

				base = input_output_set[0];

				i = 1;
				dist = 1;

				while(i<input_output_set.size()){
					if(check_ajacent(input_output_set[i],base,0,0,0,dist)){
						temp_path.push_back(input_output_set[i]);
						dist++;
					}
					else{
						if(temp_path.size()>1){
							potentialBatches.push_back(temp_path);
						}
						base = input_output_set[i];
						temp_path.clear();
						temp_path.push_back(input_output_set[i]);
						dist = 1;

					}

					i++;
				}

				if(temp_path.size()>1){
					potentialBatches.push_back(temp_path);
				}
			}




			// Honrizontal to Vertical
			sort(input_output_set.begin(),input_output_set.end(),in_row_out_col);

			temp_path.clear();
			temp_path.push_back(input_output_set[0]);

			base = input_output_set[0];

			i = 1;
			dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,0,dist,dist,0)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}

			// One to Vertical
			if(editOpType != MAP_TYPE_SPL && editOpType != MAP_TYPE_MER){

				temp_path.clear();
				temp_path.push_back(input_output_set[0]);

				base = input_output_set[0];

				i = 1;
				dist = 1;

				while(i<input_output_set.size()){
					if(check_ajacent(input_output_set[i],base,0,0,dist,0)){
						temp_path.push_back(input_output_set[i]);
						dist++;
					}
					else{
						if(temp_path.size()>1){
							potentialBatches.push_back(temp_path);
						}
						base = input_output_set[i];
						temp_path.clear();
						temp_path.push_back(input_output_set[i]);
						dist = 1;

					}

					i++;
				}

				if(temp_path.size()>1){
					potentialBatches.push_back(temp_path);
				}
			}

			// Vertical to Horizontal
			sort(input_output_set.begin(),input_output_set.end(),in_col_out_row);

			temp_path.clear();
			temp_path.push_back(input_output_set[0]);

			base = input_output_set[0];

			i = 1;
			dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,dist,0,0,dist)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}

			// Vertical to Horizontal (2)
			sort(input_output_set.begin(),input_output_set.end(),out_row_in_col);

			temp_path.clear();
			temp_path.push_back(input_output_set[0]);

			base = input_output_set[0];

			i = 1;
			dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,dist,0,0,dist)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}




			// Vertical to Vertical
			sort(input_output_set.begin(),input_output_set.end(),in_col_out_col);

			temp_path.clear();
			temp_path.push_back(input_output_set[0]);

			base = input_output_set[0];

			i = 1;
			dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,dist,0,dist,0)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}


			// Vertical to Vertical (2)
			sort(input_output_set.begin(),input_output_set.end(),out_col_in_col);

			temp_path.clear();
			temp_path.push_back(input_output_set[0]);

			base = input_output_set[0];

			i = 1;
			dist = 1;

			while(i<input_output_set.size()){
				if(check_ajacent(input_output_set[i],base,dist,0,dist,0)){
					temp_path.push_back(input_output_set[i]);
					dist++;
				}
				else{
					if(temp_path.size()>1){
						potentialBatches.push_back(temp_path);
					}
					base = input_output_set[i];
					temp_path.clear();
					temp_path.push_back(input_output_set[i]);
					dist = 1;

				}

				i++;
			}

			if(temp_path.size()>1){
				potentialBatches.push_back(temp_path);
			}

		}
		else if(editOpType == MAP_TYPE_RM){
			std::map<int,std::vector<std::tuple<int,int,int,int>>> colMap;

			// Group by column
			for(std::tuple<int,int,int,int> t:input_output_set){
				int col = get<1>(t);
				colMap[col].push_back(t);
			}

			for(std::map<int,std::vector<std::tuple<int,int,int,int>>>::iterator it2 = colMap.begin(); it2 != colMap.end(); it2++){
				std::vector<std::tuple<int,int,int,int>> temp_batch = it2->second;

				std::vector<std::tuple<int,int,int,int>> temp_path;

				for(std::tuple<int,int,int,int> p : temp_batch){
					temp_path.push_back(p);
				}

				if(temp_path.size()>0){
					potentialBatches.push_back(temp_path);
				}
			}

		}

	}


	// Recalculate cost

	std::vector<std::tuple<int,int,int,int>> overlap;

	sort(potentialBatches.begin(),potentialBatches.end(),larger_size);

	float batch_cost = 0;





	if(debug_level>0){

		printPath(path);

		cout<<"-----------Batches\n";

	}

	for(std::vector<std::tuple<int,int,int,int>> batch : potentialBatches){
		// Add this batch
		
		for(std::tuple<int,int,int,int> b:batch){

			if(debug_level>0)  printEditOp(pathMap[b]);
		}

		if(debug_level>0) cout<<"\n";

	}

	for(std::vector<std::tuple<int,int,int,int>> batch : potentialBatches){
		// Add this batch
		if(!CheckCommon(batch,overlap)){
			int temp_cost = 0;
				
			for(std::tuple<int,int,int,int> b:batch){

				if(debug_level>0)  printEditOp(pathMap[b]);
				temp_cost += pathMap[b].get<3>();
			}

			if(debug_level>0) cout<<"\n";

			batch_cost += temp_cost/float(batch.size());


			overlap.insert( overlap.end(), batch.begin(), batch.end() );

		}

	}

	if(debug_level>0) cout<<"----------- Remains\n";

	for(std::tuple<int,int,int,int> i : in_out_total){
		if(std::find(overlap.begin(), overlap.end(), i)== overlap.end()){
			if(debug_level>0) printEditOp(pathMap[i]);
			batch_cost += pathMap[i].get<3>();

		}
	}
	return batch_cost;
}




BOOST_PYTHON_MODULE(foofah_utils)
{
    def("cost_data_transform", cost_data_transform);
    def("tokenize", tokenize);
    def("cost_move", cost_move);
    def("cost_edit_op",cost_edit_op);
    def("get_ged",get_ged);
    def("get_ged_batch",get_ged_batch);
    class_<TableGraph>("TableGraph",init<int,int>())
    .def("addCell",&TableGraph::addCell)
    .def("size",&TableGraph::size)
    .def("printTable",&TableGraph::printTable)
    .def_readonly("num_rows", &TableGraph::num_rows)
    .def_readonly("num_cols", &TableGraph::num_cols)
        //methods and attrs here
    ;
}