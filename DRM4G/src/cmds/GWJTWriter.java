/* -------------------------------------------------------------------------- */
/* Copyright 2002-2011, GridWay Project Leads (GridWay.org)                   														*/
/*                                                                            																							*/
/* Licensed under the Apache License, Version 2.0 (the "License"); you may    														*/
/* not use this file except in compliance with the License. You may obtain    															*/
/* a copy of the License at                                                   																				*/
/*                                                                            																							*/
/* http://www.apache.org/licenses/LICENSE-2.0                                 																	*/
/*                                                                            																							*/
/* Unless required by applicable law or agreed to in writing, software        																*/
/* distributed under the License is distributed on an "AS IS" BASIS,          																*/
/* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   												*/
/* See the License for the specific language governing permissions and        															*/
/* limitations under the License.                                             																				*/
/* -------------------------------------------------------------------------- */


import java.io.*;
import java.util.*;

public class GWJTWriter 
{
	private	Vector	gwjtElements;
	
	private String	gwjtFileName;
	
	private File		gwjtFile;

	
	public GWJTWriter(String gwjtFileName, Vector gwjtElements)
	{
		this.gwjtFileName = gwjtFileName;
		this.gwjtElements = gwjtElements;
	}
	
	public void generateFile()
	{
		try
		{
			String 					text = new String ("#This file was automatically generated by the jsdl2gw command\n");
			FileOutputStream 	gwjtStream=null;

			
			if (this.gwjtFileName != null)
			{
				this.gwjtFile = new File(this.gwjtFileName);
				gwjtStream= new FileOutputStream(this.gwjtFile);
				gwjtStream.write(text.getBytes());
			}
			else
				System.out.println(text);
			
			for (int i=0; i<this.gwjtElements.size(); i++)
			{
				GWJTElement gwjtElement = (GWJTElement) this.gwjtElements.get(i);
		
				text = new String("");
				
				if (gwjtElement.getName()!=null)
					text+=gwjtElement.getName()+ "="; 
				
				if (gwjtElement.getValue()!=null && !text.equals(""))
					text+=gwjtElement.getValue()+ "\n";
				
				if (this.gwjtFileName != null && !text.equals(""))
					gwjtStream.write(text.getBytes());
				else if (!text.equals(""))
					System.out.print(text);
			}	
			
			if (this.gwjtFileName!=null)
				gwjtStream.close();
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
	}
	
}
